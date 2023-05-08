<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20230506214643 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE redirect (id INT AUTO_INCREMENT NOT NULL, https_id INT NOT NULL, name VARCHAR(255) NOT NULL, domains LONGTEXT NOT NULL COMMENT \'(DC2Type:array)\', active TINYINT(1) NOT NULL, url VARCHAR(255) NOT NULL, INDEX IDX_C30C9E2BF7E02C17 (https_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE redirect ADD CONSTRAINT FK_C30C9E2BF7E02C17 FOREIGN KEY (https_id) REFERENCES https_type (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP TABLE redirect');
    }
}
