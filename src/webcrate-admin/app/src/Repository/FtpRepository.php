<?php

namespace App\Repository;

use App\Entity\Ftp;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Ftp|null find($id, $lockMode = null, $lockVersion = null)
 * @method Ftp|null findOneBy(array $criteria, array $orderBy = null)
 * @method Ftp[]    findAll()
 * @method Ftp[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class FtpRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Ftp::class);
    }

    // /**
    //  * @return Ftp[] Returns an array of Ftp objects
    //  */
    /*
    public function findByExampleField($value)
    {
        return $this->createQueryBuilder('f')
            ->andWhere('f.exampleField = :val')
            ->setParameter('val', $value)
            ->orderBy('f.id', 'ASC')
            ->setMaxResults(10)
            ->getQuery()
            ->getResult()
        ;
    }
    */

    /*
    public function findOneBySomeField($value): ?Ftp
    {
        return $this->createQueryBuilder('f')
            ->andWhere('f.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
