<?php

namespace App\Repository;

use App\Entity\HttpsType;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method HttpsType|null find($id, $lockMode = null, $lockVersion = null)
 * @method HttpsType|null findOneBy(array $criteria, array $orderBy = null)
 * @method HttpsType[]    findAll()
 * @method HttpsType[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class HttpsTypeRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, HttpsType::class);
    }

    public function findById($id): ?HttpsType
    {
        return $this->createQueryBuilder('h')
            ->andWhere('h.id = :val')
            ->setParameter('val', $id)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }

    public function findByName($name): ?HttpsType
    {
        return $this->createQueryBuilder('h')
            ->andWhere('h.name = :val')
            ->setParameter('val', $name)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }

    /**
     * @return HttpsType[] Returns an array of HttpsType objects
     */
    public function getList()
    {
        return $this->createQueryBuilder('ht')
            ->orderBy('ht.id', 'ASC')
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
        return $this->createQueryBuilder('ht')
            ->orderBy('ht.id', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getArrayResult()
        ;
    }


}
