<?php

namespace App\Repository;

use App\Entity\NginxTemplate;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method NginxTemplate|null find($id, $lockMode = null, $lockVersion = null)
 * @method NginxTemplate|null findOneBy(array $criteria, array $orderBy = null)
 * @method NginxTemplate[]    findAll()
 * @method NginxTemplate[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class NginxTemplateRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, NginxTemplate::class);
    }

    public function findByName($name): ?NginxTemplate
    {
        return $this->createQueryBuilder('n')
            ->andWhere('n.name = :name')
            ->setParameter('name', $name)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }

}
