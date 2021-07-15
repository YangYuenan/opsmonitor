
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for cfgnotify
-- ----------------------------
DROP TABLE IF EXISTS `cfgnotify`;
CREATE TABLE `cfgnotify`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `notify_type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `notify_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `notify_number` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for globalcfg
-- ----------------------------
DROP TABLE IF EXISTS `globalcfg`;
CREATE TABLE `globalcfg`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `smtp_server` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `smtp_port` smallint(6) NOT NULL,
  `smtp_user` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `smtp_password_base64` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `inspect_interval` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for hostinfo
-- ----------------------------
DROP TABLE IF EXISTS `hostinfo`;
CREATE TABLE `hostinfo`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `host_ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `host_port` smallint(6) NOT NULL,
  `host_user` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `host_password_base64` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for itemstatus
-- ----------------------------
DROP TABLE IF EXISTS `itemstatus`;
CREATE TABLE `itemstatus`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `host_ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `item_id` int(11) NOT NULL,
  `item_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `check_time` datetime NOT NULL,
  `item_detail` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `warning_status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_item_check_time`(`id`, `item_id`, `item_name`, `item_detail`, `check_time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for monitoritem
-- ----------------------------
DROP TABLE IF EXISTS `monitoritem`;
CREATE TABLE `monitoritem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `warning_value` smallint(6) NOT NULL,
  `tcp_http` varchar(255) NOT NULL DEFAULT '0',
  `matching_char` varchar(255) NOT NULL,
  `notify_user` varchar(255) DEFAULT NULL,
  `check_time` datetime DEFAULT NULL,
  `item_detail` varchar(255) DEFAULT NULL,
  `item_status` tinyint(1) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `monitoritem_host_id` (`host_id`),
  CONSTRAINT `monitoritem_hostinfo_id` FOREIGN KEY (`host_id`) REFERENCES `hostinfo` (`id`)
) ENGINE=InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `fullname` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `phone` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', 'pbkdf2:sha1:1000$Km1vdx3W$9aa07d3b79ab88aae53e45d26d0d4d4e097a6cd3', '管理员', 'admin@admin.com', '12345678901', 1);

SET FOREIGN_KEY_CHECKS = 1;
