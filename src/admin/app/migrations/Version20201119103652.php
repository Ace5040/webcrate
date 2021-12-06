<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20201119103652 extends AbstractMigration
{
    public function getDescription() : string
    {
        return '';
    }

    public function up(Schema $schema) : void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE backend (id INT AUTO_INCREMENT NOT NULL, name VARCHAR(32) NOT NULL, version VARCHAR(32) NOT NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE https_type (id INT AUTO_INCREMENT NOT NULL, name VARCHAR(255) NOT NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE project (id INT AUTO_INCREMENT NOT NULL, https_id INT NOT NULL, backend_id INT NOT NULL, name VARCHAR(255) NOT NULL, uid BIGINT NOT NULL, domains LONGTEXT NOT NULL COMMENT \'(DC2Type:array)\', password VARCHAR(255) NOT NULL, nginx_config TINYINT(1) NOT NULL, root_folder VARCHAR(255) NOT NULL, mysql TINYINT(1) NOT NULL, mysql5 TINYINT(1) NOT NULL, postgre TINYINT(1) NOT NULL, backup TINYINT(1) NOT NULL, gunicorn_app_module VARCHAR(255) DEFAULT NULL, INDEX IDX_2FB3D0EEF7E02C17 (https_id), INDEX IDX_2FB3D0EEF92ABD28 (backend_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE project ADD CONSTRAINT FK_2FB3D0EEF7E02C17 FOREIGN KEY (https_id) REFERENCES https_type (id)');
        $this->addSql('ALTER TABLE project ADD CONSTRAINT FK_2FB3D0EEF92ABD28 FOREIGN KEY (backend_id) REFERENCES backend (id)');
        $this->addSql('ALTER TABLE user CHANGE roles roles LONGTEXT NOT NULL COMMENT \'(DC2Type:json)\'');
    }

    public function down(Schema $schema) : void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE project DROP FOREIGN KEY FK_2FB3D0EEF92ABD28');
        $this->addSql('ALTER TABLE project DROP FOREIGN KEY FK_2FB3D0EEF7E02C17');
        $this->addSql('DROP TABLE backend');
        $this->addSql('DROP TABLE https_type');
        $this->addSql('DROP TABLE project');
        $this->addSql('ALTER TABLE user CHANGE roles roles LONGTEXT CHARACTER SET utf8mb4 NOT NULL COLLATE `utf8mb4_bin`');
    }
}
