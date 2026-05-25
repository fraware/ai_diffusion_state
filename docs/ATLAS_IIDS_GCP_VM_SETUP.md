# Atlas IIDS — Google Cloud VM setup

Use this guide when production runs on **Google Compute Engine** (GCE).

## Your current instance (do not use for IIDS as-is)

| Field | Current value | Required for IIDS |
|-------|---------------|-------------------|
| Name | `instance-20260404-132109` | any |
| Zone | `us-central1-a` | same region OK |
| External IP | `34.135.155.151` | SSH access |
| Machine type | **e2-medium** (2 vCPU, ~4 GB RAM) | **8+ vCPU, 32 GB RAM** |
| Boot disk | **10 GB** Debian 12 | **50 GB** boot + **500 GB data** |
| Data mount | none | `/mnt/iids_sources` with **>= 300 GB free** |

**Do not** run `make atlas-iids-cloud STEP=detail` on the 10 GB boot disk. The SQL file alone is ~136 GB; conversion and cache need more space.

---

## Recommended approach (two options)

### Option A — New dedicated VM (cleanest)

Create a production VM in the same project/zone:

```bash
gcloud config set project pf-swe-bench

gcloud compute instances create atlas-iids-prod \
  --zone=us-central1-a \
  --machine-type=e2-standard-8 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --create-disk=size=500GB,type=pd-balanced,auto-delete=yes,name=atlas-iids-data \
  --disk=name=atlas-iids-data,device-name=iids-data,mode=rw,auto-delete=yes \
  --tags=http-server,https-server

gcloud compute ssh atlas-iids-prod --zone=us-central1-a
```

On the VM, format and mount the data disk (if not auto-mounted):

```bash
sudo bash scripts/gcp_setup_iids_data_disk.sh
```

Then continue with [cloud VM engineer instructions](ATLAS_IIDS_CLOUD_VM_ENGINEER_INSTRUCTIONS.md).

### Option B — Upgrade existing instance + attach data disk

**1. Stop the instance** (required to change machine type):

```bash
gcloud compute instances stop instance-20260404-132109 --zone=us-central1-a
```

**2. Resize machine type** (example: 8 vCPU, 32 GB RAM):

```bash
gcloud compute instances set-machine-type instance-20260404-132109 \
  --zone=us-central1-a \
  --machine-type=e2-standard-8
```

Alternatives: `n2-standard-8`, `c3-standard-8` (check quota/cost).

**3. Create and attach a 500 GB data disk:**

```bash
gcloud compute disks create atlas-iids-data \
  --project=pf-swe-bench \
  --zone=us-central1-a \
  --size=500GB \
  --type=pd-balanced

gcloud compute instances attach-disk instance-20260404-132109 \
  --disk=atlas-iids-data \
  --zone=us-central1-a \
  --device-name=iids-data
```

**4. Start the instance:**

```bash
gcloud compute instances start instance-20260404-132109 --zone=us-central1-a
```

**5. SSH and mount the data disk:**

```bash
gcloud compute ssh instance-20260404-132109 --zone=us-central1-a
```

On the VM:

```bash
git clone https://github.com/fraware/ai_diffusion_state.git
cd ai_diffusion_state
git pull
sudo bash scripts/gcp_setup_iids_data_disk.sh
bash scripts/cloud_vm_bootstrap.sh
```

---

## SSH from Windows (control laptop)

```powershell
gcloud compute ssh instance-20260404-132109 --zone=us-central1-a --project=pf-swe-bench
```

Or with plain SSH (if you added your key):

```powershell
ssh -i PATH_TO_KEY username@34.135.155.151
```

Debian 12 default user is often your Google account username or `debian` — use `gcloud compute ssh` to avoid guessing.

---

## Firewall (if download fails)

OpenXLab uses HTTPS outbound only. Default VPC usually allows egress. If downloads stall, confirm no restrictive firewall rule blocks egress on TCP 443.

Optional: allow SSH from your IP only:

```bash
gcloud compute firewall-rules create allow-ssh-atlas-iids \
  --allow=tcp:22 \
  --source-ranges=YOUR_PUBLIC_IP/32 \
  --target-tags=atlas-iids
```

---

## Production on the VM (after disk + bootstrap)

```bash
export OPENXLAB_AK="YOUR_ROTATED_KEY"
export OPENXLAB_SK="YOUR_ROTATED_SECRET"
export OPENXLAB_IIDS_SOURCES_DIR=/mnt/iids_sources
export OPENXLAB_INSECURE_SSL=1
export PYTHONUTF8=1

tmux new -s iids
cd ~/ai_diffusion_state && source .venv/bin/activate

make atlas-iids-cloud STEP=status    # must show >= 300 GB free at /mnt/iids_sources
make atlas-iids-cloud STEP=docs
make atlas-iids-cloud STEP=detail
make atlas-iids-cloud STEP=smoke-convert
make atlas-iids-cloud STEP=full-convert
make atlas-iids-cloud-copyback
```

Copy tarball to laptop:

```bash
# On VM — path to tarball
ls -lh atlas_iids_filtered_outputs.tar.gz

# On laptop (PowerShell)
gcloud compute scp instance-20260404-132109:~/ai_diffusion_state/atlas_iids_filtered_outputs.tar.gz . `
  --zone=us-central1-a --project=pf-swe-bench
```

Then:

```powershell
powershell -File scripts\import_iids_copyback.ps1 -TarballPath .\atlas_iids_filtered_outputs.tar.gz
```

---

## Cost note (rough order of magnitude)

- `e2-standard-8` in `us-central1`: compute + 500 GB `pd-balanced` for several days of download/convert
- Stop or delete the VM after copy-back to avoid ongoing charges
- Use `--auto-delete=yes` on the data disk if the VM is ephemeral

---

## Preflight on VM

```bash
bash scripts/gcp_vm_preflight.sh
```

Fails closed if RAM, CPU count, or `/mnt/iids_sources` free space is insufficient.
