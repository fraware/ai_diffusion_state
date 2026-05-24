CREATE TABLE `base_patent_law_status` (
  `pn` varchar(64),
  `event_date` varchar(16),
  `authorize` int,
  `reject` int,
  `event_code` varchar(16),
  `code_expl` varchar(128),
  `transfer` int,
  `invalid` int
);

INSERT INTO `base_patent_law_status` VALUES
('CN2018123456A','20200615',1,0,'GR01','GRANT',0,0),
('CN2019234567A','20210320',1,0,'GR01','GRANT',0,0);
