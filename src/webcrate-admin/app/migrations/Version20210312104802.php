<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20210312104802 extends AbstractMigration
{
    public function getDescription() : string
    {
        return '';
    }

    public function up(Schema $schema) : void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE nginx_template (id INT AUTO_INCREMENT NOT NULL, name VARCHAR(255) NOT NULL, label VARCHAR(255) NOT NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE project ADD nginx_template_id INT, DROP nginx_config');
        $this->addSql('ALTER TABLE project ADD CONSTRAINT FK_2FB3D0EE8CD97732 FOREIGN KEY (nginx_template_id) REFERENCES nginx_template (id)');
        $this->addSql('CREATE INDEX IDX_2FB3D0EE8CD97732 ON project (nginx_template_id)');
    }

    public function down(Schema $schema) : void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE project DROP FOREIGN KEY FK_2FB3D0EE8CD97732');
        $this->addSql('DROP TABLE nginx_template');
        $this->addSql('DROP INDEX IDX_2FB3D0EE8CD97732 ON project');
        $this->addSql('ALTER TABLE project ADD nginx_config TINYINT(1) NOT NULL, DROP nginx_template_id');
    }
}
