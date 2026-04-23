<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260410000001 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add customModules JSON column to project table for modular Docker image support';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE project ADD custom_modules JSON DEFAULT NULL COMMENT \'(DC2Type:json)\'');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE project DROP COLUMN custom_modules');
    }
}
