<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20210323231931 extends AbstractMigration
{
    public function getDescription() : string
    {
        return '';
    }

    public function up(Schema $schema) : void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ftp ADD project_id INT NOT NULL');
        $this->addSql('ALTER TABLE ftp ADD CONSTRAINT FK_A84DA34E166D1F9C FOREIGN KEY (project_id) REFERENCES project (id)');
        $this->addSql('CREATE INDEX IDX_A84DA34E166D1F9C ON ftp (project_id)');
    }

    public function down(Schema $schema) : void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ftp DROP FOREIGN KEY FK_A84DA34E166D1F9C');
        $this->addSql('DROP INDEX IDX_A84DA34E166D1F9C ON ftp');
        $this->addSql('ALTER TABLE ftp DROP project_id');
    }
}
