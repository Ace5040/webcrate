<?php

namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use App\Entity\HttpsType;
class HttpsTypes extends Fixture
{

    public function load(ObjectManager $manager)
    {

        $types = [
            'disabled',
            'letsencrypt',
            'openssl'
        ];

        foreach ($types as $type) {

            $repository = $manager->getRepository(HttpsType::class);
            $typeExist = $repository->findByName($type);
            if (!$typeExist) {
                $entity = new HttpsType();
                $entity->setName($type);
                $manager->persist($entity);
            }

        }
        $manager->flush();
    }
}
