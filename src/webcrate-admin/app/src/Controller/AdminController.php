<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use Symfony\Component\Yaml\Yaml;
use Symfony\Component\HttpClient\CurlHttpClient;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Serializer\Encoder\JsonEncoder;
use Symfony\Contracts\Cache\ItemInterface;
use Symfony\Contracts\Cache\CacheInterface;
use App\Repository\ProjectRepository;
use App\Repository\HttpsTypeRepository;
use App\Repository\BackendRepository;
use App\Repository\NginxTemplateRepository;
use App\Entity\Project;
use App\Entity\HttpsType;
use App\Entity\Backend;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\Filesystem\Exception\IOExceptionInterface;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Validator\Constraints\Type;
use Symfony\Component\Form\Extension\Core\Type\DateType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\CollectionType;
use App\Form\Type\DomainsType;
use App\Form\Type\DomainType;
use App\Form\Type\ProjectType;
use App\Entity\Ftp;

class AdminController extends AbstractController
{

    private $cache;
    private $repository;
    private $https_repository;
    private $backend_repository;
    private $nginx_tempalte_repository;

    public function __construct(CacheInterface $cache, ProjectRepository $repository, HttpsTypeRepository $https_repository, BackendRepository $backend_repository, NginxTemplateRepository $nginx_template_repository, EntityManagerInterface $manager)
    {
        $this->cache = $cache;
        $this->repository = $repository;
        $this->https_repository = $https_repository;
        $this->backend_repository = $backend_repository;
        $this->nginx_template_repository = $nginx_template_repository;
        $this->manager = $manager;
    }

    /**
     * @Route("/", name="admin")
     */
    public function index()
    {
        $soft = $this->cache->get('versions', function (ItemInterface $item) {
            $item->expiresAfter(604800);
            return $this->getVersions();
        });
        $sha256sum = $this->getSha256Sum();
        $actual_sha256sum = $this->getActualSha256Sum();
        return $this->render('admin/index.html.twig', [
            'controller_name' => 'AdminController',
            'actual' => $sha256sum === $actual_sha256sum,
            'currentsha256' => $sha256sum,
            'actualsha256' => $actual_sha256sum,
            'soft' => $soft
        ]);
    }

    private function getVersions()
    {
        $process = Process::fromShellCommandline('sudo /webcrate/versions.py');
        $process->run();
        if (!$process->isSuccessful()) {
            throw new \Symfony\Component\Process\Exception\ProcessFailedException($process);
        }
        $soft_json = $process->getOutput();
        $encoder = new JsonEncoder();
        $soft = [];
        if(!empty($soft_json))
        {
            $soft = $encoder->decode($soft_json, 'json');
        }
        return $soft;
    }

    /**
     * @Route("/admin/projects", name="admin-projects")
     */
    public function projects()
    {
        $list = $this->repository->getListForTable();
        $sha256sum = $this->getSha256Sum();
        $actual_sha256sum = $this->getActualSha256Sum();
        return $this->render('admin/projects.html.twig', [
            'controller_name' => 'AdminController',
            'projects' => $list,
            'actual' => $sha256sum === $actual_sha256sum
        ]);
    }

    /**
     * @Route("/admin/project/add", name="project-add")
     */
    public function newProject(Request $request)
    {
        $project = new Project();
        $form = $this->createForm(ProjectType::class, $project);
        if ($request->isMethod('POST'))
        {
            $form->handleRequest($request);
            if ($form->isSubmitted() && $form->isValid())
            {
                $project = $form->getData();
                $project->setUid($this->repository->getFirstAvailableUid());
                $ftps = $project->getFtps();
                foreach ( $ftps as $ftp ) {
                    $ftp->setProject($project);
                }
                $this->manager->persist($project);
                $this->manager->flush();
                $this->updateUsersYaml();
                return $this->redirectToRoute('admin-projects');
            }
        }
        $sha256sum = $this->getSha256Sum();
        $actual_sha256sum = $this->getActualSha256Sum();
        return $this->render(
            'admin/project.html.twig',
            [
                'form' => $form->createView(),
                'actual' => $sha256sum === $actual_sha256sum
            ]
        );
    }

    /**
     * @Route("/admin/project/{uid}", name="admin-project")
     */
    public function project($uid, Request $request)
    {
        $project = $this->repository->loadByUid($uid);
        $form = $this->createForm(ProjectType::class, $project);
        if ($request->isMethod('POST'))
        {
            $form->handleRequest($request);
            if ($form->isSubmitted() && $form->isValid())
            {
                $project = $form->getData();
                $ftps = $project->getFtps();
                foreach ( $ftps as $ftp ) {
                    $ftp->setProject($project);
                }
                $this->manager->persist($project);
                $this->manager->flush();
                $this->updateUsersYaml();
                return $this->redirectToRoute('admin-projects');
            }
        }
        $sha256sum = $this->getSha256Sum();
        $actual_sha256sum = $this->getActualSha256Sum();
        return $this->render(
            'admin/project.html.twig',
            [
                'form' => $form->createView(),
                'actual' => $sha256sum === $actual_sha256sum
            ]
        );
    }

    /**
     * @Route("/admin/project/{uid}/delete", name="admin-project-delete")
     */
    public function projectDelete($uid)
    {
        $project = $this->repository->loadByUid($uid);
        $this->manager->remove($project);
        $this->manager->flush();
        $list = $this->repository->getListForTable();
        $sha256sum = $this->updateUsersYaml();
        $actual_sha256sum = $this->getActualSha256Sum();
        $response = new JsonResponse();
        $response->setData([
            'result' => 'ok',
            'projects' => $list,
            'actual' => $sha256sum === $actual_sha256sum
        ]);
        return $response;
    }

    /**
     * @Route("/admin/project/{uid}/activate", name="admin-project-activate")
     */
    public function projectActivate($uid)
    {
        $project = $this->repository->loadByUid($uid);
        $project->setActive(true);
        $this->manager->flush();
        $list = $this->repository->getListForTable();
        $sha256sum = $this->updateUsersYaml();
        $actual_sha256sum = $this->getActualSha256Sum();
        $response = new JsonResponse();
        $response->setData([
            'result' => 'ok',
            'projects' => $list,
            'actual' => $sha256sum === $actual_sha256sum
        ]);
        return $response;
    }

    /**
     * @Route("/admin/reload-config", name="admin-reload-config")
     */
    public function projectReloadConfig()
    {
        $sha256sum = $this->getSha256Sum();
        $actual_sha256sum = $this->getActualSha256Sum();
        if ( $sha256sum !== $actual_sha256sum ) {
            try {
                $process = Process::fromShellCommandline('sudo /webcrate/reload.py');
                $process->run();
                if (!$process->isSuccessful()) {
                    throw new \Symfony\Component\Process\Exception\ProcessFailedException($process);
                }
            } catch (IOExceptionInterface $exception) {
                $debug['error'] = $exception->getMessage();
            }
            $sha256sum = $this->getSha256Sum();
            $actual_sha256sum = $this->getActualSha256Sum();
        }
        $response = new JsonResponse();
        $response->setData([
            'result' => 'ok',
            'actual' => $sha256sum === $actual_sha256sum
        ]);
        return $response;
    }

    /**
     * @Route("/admin/project/{uid}/deactivate", name="admin-project-deactivate")
     */
    public function projectDeactivate($uid)
    {
        $project = $this->repository->loadByUid($uid);
        $project->setActive(false);
        $this->manager->flush();
        $list = $this->repository->getListForTable();
        $sha256sum = $this->updateUsersYaml();
        $actual_sha256sum = $this->getActualSha256Sum();
        $response = new JsonResponse();
        $response->setData([
            'result' => 'ok',
            'projects' => $list,
            'actual' => $sha256sum === $actual_sha256sum
        ]);
        return $response;
    }

    /**
     * @Route("/admin/import-projects", name="import-projects")
     */
    public function importProjects(Request $request): Response
    {
        $file = $request->files->get('file');
        $filename = $file->getClientOriginalName();
        $filepath = $file->getPathname();
        $projects = Yaml::parseFile($filepath);
        foreach ( $projects as $projectname => $project_obj ) {
            $project_obj = (object)$project_obj;
            $entity = $this->repository->loadByUid($project_obj->uid);
            if ( empty($entity) ) {
                $project = new Project();
                $project_obj->redirect = !empty($project_obj->redirect) ? $project_obj->redirect : false;
                $project_obj->backup = !empty($project_obj->backup) ? $project_obj->backup : false;
                $project_obj->gzip = !empty($project_obj->gzip) ? $project_obj->gzip : false;
                $project_obj->mysql_db = !empty($project_obj->mysql_db) ? $project_obj->mysql_db : false;
                $project_obj->mysql5_db = !empty($project_obj->mysql5_db) ? $project_obj->mysql5_db : false;
                $project_obj->postgresql_db = !empty($project_obj->postgresql_db) ? $project_obj->postgresql_db : false;
                $project_obj->root_folder = !empty($project_obj->root_folder) ? $project_obj->root_folder : 'data';
                $project_obj->password = !empty($project_obj->password) ? $project_obj->password : 'empty_password';
                $project_obj->https = !empty($project_obj->https) ? $project_obj->https : 'disabled';
                $project_obj->backend = !empty($project_obj->backend) ? $project_obj->backend : 'php';
                $project_obj->backend_version = !empty($project_obj->backend_version) ? $project_obj->backend_version : 'latest';
                $project_obj->gunicorn_app_module = !empty($project_obj->gunicorn_app_module) ? $project_obj->gunicorn_app_module : '';
                $project_obj->nginx_template = !empty($project_obj->nginx_template) ? $project_obj->nginx_template : 'default';
                $project_obj->volume = !empty($project_obj->volume) ? $project_obj->volume : 0;
                $project_obj->nginx_block = !empty($project_obj->nginx_block) ? $project_obj->nginx_block : '';
                $project_obj->domains = !empty($project_obj->domains) ? $project_obj->domains : [$projectname . '.test'];
                $project_obj->nginx_options = !empty($project_obj->nginx_options) ? $project_obj->nginx_options : [];
                $project_obj->auth_locations = !empty($project_obj->auth_locations) ? $project_obj->auth_locations : [];
                $project_obj->duplicity_filters = !empty($project_obj->duplicity_filters) ? $project_obj->duplicity_filters : [];
                $project_obj->ftps = !empty($project_obj->ftps) ? $project_obj->ftps : [];
                $project->setUid($project_obj->uid);
                $project->setName($projectname);
                $project->setVolume($project_obj->volume);
                $project->setBackup($project_obj->backup == 'yes' || $project_obj->backup === true);
                $project->setRedirect($project_obj->redirect == 'yes' || $project_obj->redirect === true);
                $project->setGzip($project_obj->gzip == 'yes' || $project_obj->gzip === true);
                $project->setMysql($project_obj->mysql_db == 'yes' || $project_obj->mysql_db === true);
                $project->setMysql5($project_obj->mysql5_db == 'yes' || $project_obj->mysql5_db === true);
                $project->setPostgre($project_obj->postgresql_db == 'yes' || $project_obj->postgresql_db === true);
                $project->setRootFolder($project_obj->root_folder);
                $project->setPasswordHash($project_obj->password);
                $https = $this->https_repository->findByName($project_obj->https);
                $project->setHttps($https);
                $backend_version = empty($project_obj->backend_version) || $project_obj->backend_version == "7" ? 'latest' : $project_obj->backend_version;
                $backend = $this->backend_repository->findByNameAndVersion($project_obj->backend, (string)$backend_version);
                $project->setBackend($backend);
                if ( !empty($project_obj->gunicorn_app_module) && ( $project_obj->backend == 'gunicorn' ) ) {
                    $project->setGunicornAppModule($project_obj->gunicorn_app_module);
                }
                $template = $this->nginx_template_repository->findByName($project_obj->nginx_template);
                $project->setNginxTemplate($template);
                $project->setNginxBlock($project_obj->nginx_block);
                $project->setDomains($project_obj->domains);
                $options_array = [];
                foreach ( $project_obj->nginx_options as $name => $value ) {
                    $options_array[] = [ 'name' => $name, 'value' => $value ];
                }
                $project->setNginxOptions($options_array);
                $locations_array = [];
                foreach ( $project_obj->auth_locations as $location ) {
                    $locations_array[] = [
                        'path' => $location['path'],
                        'title' => $location['title'],
                        'user' => $location['user'],
                        'password' => $location['password']
                    ];
                }
                $project->setAuthLocations($locations_array, true);
                $duplicity_filters_array = [];
                foreach ( $project_obj->duplicity_filters as $filter ) {
                    $duplicity_filters_array[] = [
                        'mode' => $filter['mode'],
                        'path' => $filter['path']
                    ];
                }
                $project->setDuplicityFilters($duplicity_filters_array, true);
                foreach ( $project_obj->ftps as $ftp_data ) {
                    $ftp = new Ftp();
                    $ftp->setName($ftp_data['name']);
                    $ftp->setPasswordHash($ftp_data['password']);
                    $ftp->setHome($ftp_data['home']);
                    $project->addFtp($ftp);
                }

                $this->manager->persist($project);
            }
        }
        $this->manager->flush();
        $sha256sum = $this->updateUsersYaml();
        $actual_sha256sum = $this->getActualSha256Sum();
        $list = $this->repository->getListForTable();
        $response = new JsonResponse();
        $response->setData([
            'result' => 'ok',
            'projects' => $list,
            'actual' => $sha256sum === $actual_sha256sum
        ]);

        return $response;
    }

    public function updateUsersYaml()
    {
        $ymlData = $this->getYmlData();
        $sha256sum = hash('sha256', $ymlData);
        try {
            $new_file_path = "/webcrate/updated-users.yml";
            file_put_contents($new_file_path, $ymlData);
            $process = Process::fromShellCommandline('sudo /webcrate/updateusers.py');
            $process->run();
            if (!$process->isSuccessful()) {
                throw new \Symfony\Component\Process\Exception\ProcessFailedException($process);
            }
        } catch (IOExceptionInterface $exception) {
            $debug['error'] = $exception->getMessage();
        }

        return $sha256sum;
    }

    public function getYmlData()
    {
        $projects = $this->repository->getList();
        $projects_list = (object)[];
        foreach ( $projects as $project ) {
            if ( $project->getActive() ) {
                $projectname = $project->getName();
                $projects_list->$projectname = $project->toObject();
            }
        }
        $ymlData = Yaml::dump($projects_list, 3, 2, Yaml::DUMP_OBJECT_AS_MAP);
        return $ymlData;
    }

    public function getSha256Sum()
    {
        $ymlData = $this->getYmlData();
        $sha256sum = hash('sha256', $ymlData);
        return $sha256sum;
    }

    public function getActualSha256Sum()
    {
        $sha256sum = file_get_contents('/webcrate/meta/projects.checksum');
        return $sha256sum;
    }

}
