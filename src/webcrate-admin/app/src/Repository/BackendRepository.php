<?php

namespace App\Repository;

use App\Entity\Backend;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Backend|null find($id, $lockMode = null, $lockVersion = null)
 * @method Backend|null findOneBy(array $criteria, array $orderBy = null)
 * @method Backend[]    findAll()
 * @method Backend[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class BackendRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Backend::class);
    }

    public function findByNameAndVersion($name, $version): ?Backend
    {
        return $this->createQueryBuilder('b')
            ->andWhere('b.name = :val')
            ->setParameter('val', $name)
            ->andWhere('b.version = :val2')
            ->setParameter('val2', $version)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }

    /**
     * @return Backend[] Returns an array of Backend objects
     */
    public function getList()
    {
        return $this->createQueryBuilder('b')
            ->orderBy('b.id', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getResult()
        ;
    }

    /**
     * @return [] Returns an array
     */
    public function getArray()
    {
        return $this->createQueryBuilder('b')
            ->orderBy('b.id', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getArrayResult()
        ;
    }

}
