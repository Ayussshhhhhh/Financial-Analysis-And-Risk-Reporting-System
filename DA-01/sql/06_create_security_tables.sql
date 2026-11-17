USE EnterpriseBI;
GO
IF OBJECT_ID('sec.UserRegionRole','U') IS NULL CREATE TABLE sec.UserRegionRole(UserEmail nvarchar(254) NOT NULL, RoleName nvarchar(40) NOT NULL, RegionName nvarchar(50) NULL, CONSTRAINT PK_UserRegionRole PRIMARY KEY(UserEmail,RoleName,RegionName));
IF NOT EXISTS(SELECT 1 FROM sec.UserRegionRole) INSERT sec.UserRegionRole(UserEmail,RoleName,RegionName) VALUES
('north.america.manager@example.com','RegionalManager','North America'),('europe.manager@example.com','RegionalManager','Europe'),('pacific.manager@example.com','RegionalManager','Pacific'),('cfo@example.com','Finance',NULL),('hr.manager@example.com','HR',NULL),('supply.chain@example.com','SupplyChain',NULL),('ceo@example.com','Executive',NULL);
GO
