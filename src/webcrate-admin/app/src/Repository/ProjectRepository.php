<?php

namespace App\Repository;

use App\Entity\Project;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Project|null find($id, $lockMode = null, $lockVersion = null)
 * @method Project|null findOneBy(array $criteria, array $orderBy = null)
 * @method Project[]    findAll()
 * @method Project[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class ProjectRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Project::class);
    }

    /**
     * @return Project[] Returns an array of Project objects
     */
    public function getList()
    {
        return $this->createQueryBuilder('p')
            ->orderBy('p.uid', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getResult()
        ;
    }

    /**
     * @return object[] Returns an array of Project-like objects
     */
    public function getListForTable()
    {
        $projects = $this->createQueryBuilder('p')
            ->orderBy('p.uid', 'ASC')
            ->setMaxResults(1000)
            ->getQuery()
            ->getResult()
        ;
        $list = [];
        foreach ($projects as $project) {
            $item = (object)[];
            $item->name = $project->getName();
            $item->uid = $project->getUid();
            $item->backend = $project->getBackend()->getName() . ' ' . $project->getBackend()->getVersion();
            $item->backup = $project->getBackup() ? 'yes' : 'no';
            $item->https = $project->getHttps()->getName();
            $item->active = !empty($project->getActive());
            $item->template = !empty($project->getNginxTemplate()) ? $project->getNginxTemplate()->getLabel() : 'default';
            $list[] = $item;
        }
        return $list;

    }

    public function loadByUid($uid): ?Project
    {
        return $this->createQueryBuilder('p')
            ->andWhere('p.uid = :val')
            ->setParameter('val', $uid)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }

    public function getFirstAvailableUid(): ?int
    {


        $conn = $this->getEntityManager()->getConnection();

        $sql = '
            SELECT uid FROM project p
            ORDER BY p.uid ASC
            ';
        $stmt = $conn->prepare($sql);
        $stmt->execute();
        $results = $stmt->fetchAll();
        if ( !empty($results) ) {
            $freeUid = intval(end($results)['uid']) + 1;
        } else {
            $freeUid = 100000;
        }
        foreach ( $results as $index => $row ) {
            $uid = intval($row['uid']);
            if ($index + 100000 !== $uid) {
                $freeUid = $index + 100000;
                break;
            }
        }
        return $freeUid;

    }

}
