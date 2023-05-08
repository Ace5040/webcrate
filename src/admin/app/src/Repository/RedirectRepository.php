<?php

namespace App\Repository;

use App\Entity\Redirect;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Redirect|null find($id, $lockMode = null, $lockVersion = null)
 * @method Redirect|null findOneBy(array $criteria, array $orderBy = null)
 * @method Redirect[]    findAll()
 * @method Redirect[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class RedirectRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Redirect::class);
    }

    /**
     * @return Redirect[] Returns an array of Project objects
     */
    public function getList()
    {
        return $this->createQueryBuilder('r')
            ->orderBy('r.name', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getResult()
        ;
    }

    public function loadByName($name): ?Redirect
    {
        return $this->createQueryBuilder('r')
            ->andWhere('r.name = :val')
            ->setParameter('val', $name)
            ->setMaxResults(1)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }


    /**
     * @return object[] Returns an array of Project-like objects
     */
    public function getListForTable()
    {
        $redirects = $this->createQueryBuilder('r')
            ->orderBy('r.name', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getResult()
        ;
        $list = [];
        foreach ($redirects as $redirect) {
            $item = (object)[];
            $item->name = $redirect->getName();
            $item->applying = false;
            $item->https = $redirect->getHttps()->getName();
            $item->url = $redirect->getUrl();
            $item->active = !empty($redirect->getActive());
            $item->actual = $redirect->isActual();
            $item->actualSha256 = $redirect->getActualSha256Sum();
            $item->sha256 = $redirect->getSha256Sum();
            $list[] = $item;
        }
        return $list;

    }

}
