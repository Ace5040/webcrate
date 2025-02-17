<?php

namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use App\Entity\Backend;

class Backends extends Fixture
{
    public function load(ObjectManager $manager)
    {

        $backends = [
            [
                'name' => 'php',
                'version' => '83'
            ],
            [
                'name' => 'php',
                'version' => '81'
            ],
            [
                'name' => 'php',
                'version' => '74'
            ],
            [
                'name' => 'php',
                'version' => '73'
            ],
            [
                'name' => 'php',
                'version' => '56'
            ],
            [
                'name' => 'gunicorn',
                'version' => 'latest'
            ]
        ];

        foreach ($backends as $backend) {
            $name = $backend['name'];
            $version = $backend['version'];
            $repository = $manager->getRepository(Backend::class);
            $entityExist = $repository->findByNameAndVersion($name, $version);
            if (!$entityExist) {
                $entity = new Backend();
                $entity->setName($name);
                $entity->setVersion($version);
                $manager->persist($entity);
            }

        }
        $manager->flush();
    }
}
