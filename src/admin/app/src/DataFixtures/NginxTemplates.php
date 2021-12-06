<?php

namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use App\Entity\NginxTemplate;

class NginxTemplates extends Fixture
{
    public function load(ObjectManager $manager)
    {

        $templates = [
            [
                'name' => 'default',
                'label' => 'Default'
            ],
            [
                'name' => 'drupal8',
                'label' => 'Drupal 8'
            ],
            [
                'name' => 'drupal7',
                'label' => 'Drupal 7 '
            ],
            [
                'name' => 'drupal6',
                'label' => 'Drupal 6'
            ],
            [
                'name' => 'html',
                'label' => 'Html only'
            ],
            [
                'name' => 'wordpress',
                'label' => 'Wordpress'
            ],
            [
                'name' => 'opencart',
                'label' => 'Opencart'
            ]
        ];

        foreach ($templates as $template) {
            $name = $template['name'];
            $label = $template['label'];
            $repository = $manager->getRepository(NginxTemplate::class);
            $entityExist = $repository->findByName($name);
            if (!$entityExist) {
                $entity = new NginxTemplate();
                $entity->setName($name);
                $entity->setLabel($label);
                $manager->persist($entity);
            }
        }
        $manager->flush();
    }
}
