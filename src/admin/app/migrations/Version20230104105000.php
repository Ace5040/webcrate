<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20230104105000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql("UPDATE `project` SET `backend_id`=(SELECT id FROM `backend` WHERE `name`='php' AND `version`='81') WHERE `backend_id`=(SELECT id FROM `backend` WHERE `name`='php' AND `version`='latest')");
        $this->addSql("UPDATE `project` SET `backend_id`=(SELECT id FROM `backend` WHERE `name`='php' AND `version`='81') WHERE `backend_id`=(SELECT id FROM `backend` WHERE `name`='php' AND `version`='80')");
        $this->addSql("DELETE FROM `backend` WHERE `backend`.`name` = 'php' AND `backend`.`version` = 'latest'");
        $this->addSql("DELETE FROM `backend` WHERE `backend`.`name` = 'php' AND `backend`.`version` = '80'");
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
    }
}
