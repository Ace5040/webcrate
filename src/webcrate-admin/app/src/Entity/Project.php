<?php

namespace App\Entity;

use App\Repository\ProjectRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=ProjectRepository::class)
 */
class Project
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     */
    private $id;

    /**
     * @ORM\Column(type="string", length=255, unique=true)
     */
    private $name;

    /**
     * @ORM\Column(type="bigint", unique=true)
     */
    private $uid;

    /**
     * @ORM\Column(type="array")
     */
    private $domains = [];

    /**
     * @ORM\Column(type="string", length=255)
     */
    private $password;

    /**
     * @ORM\Column(type="string", length=255)
     */
    private $rootFolder;

    /**
     * @ORM\Column(type="boolean")
     */
    private $redirect;

    /**
     * @ORM\Column(type="boolean")
     */
    private $mysql;

    /**
     * @ORM\Column(type="boolean")
     */
    private $mysql5;

    /**
     * @ORM\Column(type="boolean")
     */
    private $postgre;

    /**
     * @ORM\Column(type="boolean")
     */
    private $backup;

    /**
     * @ORM\ManyToOne(targetEntity=HttpsType::class)
     * @ORM\JoinColumn(nullable=false)
     */
    private $https;

    /**
     * @ORM\ManyToOne(targetEntity=Backend::class)
     * @ORM\JoinColumn(nullable=false)
     */
    private $backend;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     */
    private $gunicornAppModule;

    /**
     * @ORM\Column(type="boolean")
     */
    private $gzip;

    /**
     * @ORM\Column(type="json")
     */
    private $nginx_options = [];

    /**
     * @ORM\Column(type="json")
     */
    private $auth_locations = [];

    /**
     * @ORM\ManyToOne(targetEntity=NginxTemplate::class)
     * @ORM\JoinColumn(nullable=true)
     */
    private $nginx_template;

    /**
     * @ORM\Column(type="text", nullable=true)
     */
    private $nginx_block;

    /**
     * @ORM\Column(type="boolean", nullable=true)
     */
    private $active;

    /**
     * @ORM\Column(type="integer", nullable=true)
     */
    private $volume;

    /**
     * @ORM\OneToMany(targetEntity=Ftp::class, mappedBy="project", orphanRemoval=true, cascade={"persist", "remove"})
     * @ORM\OrderBy({"weight" = "ASC"})
     */
    private $ftps;

    /**
     * @ORM\Column(type="json", nullable=true)
     */
    private $DuplicityFilters = [];

    public function __construct()
    {
        $this->ftps = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(string $name): self
    {
        $this->name = $name;

        return $this;
    }

    public function getUid(): ?string
    {
        return $this->uid;
    }

    public function setUid(string $uid): self
    {
        $this->uid = $uid;

        return $this;
    }

    public function getDomains(): ?array
    {
        return $this->domains;
    }

    public function setDomains(array $domains): self
    {
        $this->domains = $domains;

        return $this;
    }

    public function getPassword(): ?string
    {
        return $this->password;
    }

    public function setPassword(string $password): self
    {
        if ( !empty($password) ) {
            $salt = str_replace('+', '.', base64_encode(random_bytes(6)));
            $this->password = crypt($password, '$6$'.$salt.'$');
        }

        return $this;
    }

    public function setPasswordHash(string $password): self
    {
        if ( !empty($password) ) {
            $this->password = $password;
        }

        return $this;
    }

    public function getRootFolder(): ?string
    {
        return $this->rootFolder;
    }

    public function setRootFolder(string $rootFolder): self
    {
        $this->rootFolder = $rootFolder;

        return $this;
    }

    public function getRedirect(): ?bool
    {
        return $this->redirect;
    }

    public function setRedirect(bool $redirect): self
    {
        $this->redirect = $redirect;

        return $this;
    }

    public function getMysql(): ?bool
    {
        return $this->mysql;
    }

    public function setMysql(bool $mysql): self
    {
        $this->mysql = $mysql;

        return $this;
    }

    public function getMysql5(): ?bool
    {
        return $this->mysql5;
    }

    public function setMysql5(bool $mysql5): self
    {
        $this->mysql5 = $mysql5;

        return $this;
    }

    public function getPostgre(): ?bool
    {
        return $this->postgre;
    }

    public function setPostgre(bool $postgre): self
    {
        $this->postgre = $postgre;

        return $this;
    }

    public function getBackup(): ?bool
    {
        return $this->backup;
    }

    public function setBackup(bool $backup): self
    {
        $this->backup = $backup;

        return $this;
    }

    public function getHttps(): ?HttpsType
    {
        return $this->https;
    }

    public function setHttps(?HttpsType $https): self
    {
        $this->https = $https;

        return $this;
    }

    public function getBackend(): ?Backend
    {
        return $this->backend;
    }

    public function setBackend(?Backend $backend): self
    {
        $this->backend = $backend;

        return $this;
    }

    public function getGunicornAppModule(): ?string
    {
        return $this->gunicornAppModule;
    }

    public function setGunicornAppModule(?string $gunicornAppModule): self
    {
        $this->gunicornAppModule = $gunicornAppModule;

        return $this;
    }

    public function toObject(): object
    {
        return  (object)[
            'uid' => (int)$this->uid,
            'password' => $this->password,
            'domains' => $this->domains,
            'volume' => (int)$this->volume,
            'nginx_template' => !empty($this->nginx_template) ? $this->nginx_template->getName() : 'default',
            'nginx_block' => !empty($this->nginx_block) ? $this->nginx_block : '',
            'root_folder' => $this->rootFolder,
            'https' => !empty($this->https) ? $this->https->getName(): 'disabled',
            'backend' => !empty($this->backend) ? $this->backend->getName(): 'php',
            'backend_version' => !empty($this->backend) ? $this->backend->getVersion(): 'latest',
            'gunicorn_app_module' => !empty($this->gunicornAppModule) ? $this->gunicornAppModule : '',
            'redirect' => (bool)$this->redirect,
            'gzip' => (bool)$this->gzip,
            'nginx_options' => $this->getKeyedNginxOptions(),
            'auth_locations' => $this->getKeyedAuthLocations(),
            'ftps' => $this->getKeyedFtps(),
            'duplicity_filters' => $this->getKeyedDuplicityFilters(),
            'mysql_db' => (bool)$this->mysql,
            'mysql5_db' => (bool)$this->mysql5,
            'postgresql_db' => (bool)$this->postgre,
            'backup' => (bool)$this->backup
        ];
    }

    public function getGzip(): ?bool
    {
        return $this->gzip;
    }

    public function setGzip(bool $gzip): self
    {
        $this->gzip = $gzip;

        return $this;
    }

    public function getNginxOptions(): ?array
    {
        return $this->nginx_options;
    }

    public function getKeyedNginxOptions(): ?array
    {
        $assocArray = [];
        if ( !empty($this->nginx_options) ) {
            foreach ( $this->nginx_options as $option ) {
                $assocArray[ $option['name'] ] = $option['value'];
            }
        }
        return $assocArray;
    }

    public function setNginxOptions(array $nginx_options): self
    {
        $this->nginx_options = $nginx_options;

        return $this;
    }

    public function getAuthLocations(): ?array
    {
        return $this->auth_locations;
    }

    public function getKeyedAuthLocations(): ?array
    {
        $array = [];
        if ( !empty($this->auth_locations) ) {
            foreach ( $this->auth_locations as $location ) {
                $array[] = [
                    'path' => $location['path'],
                    'title' => $location['title'],
                    'user' => $location['user'],
                    'password' => $location['password']
                ];
            }
        }
        return $array;
    }

    public function getKeyedFtps(): ?array
    {
        $array = [];
        if ( !empty($this->ftps) ) {
            foreach ( $this->ftps as $ftp ) {
                $array[] = [
                    'name' => $ftp->getName(),
                    'password' => $ftp->getPassword(),
                    'home' => $ftp->getHome()
                ];
            }
        }
        return $array;
    }

    public function getKeyedDuplicityFilters(): ?array
    {
        $array = [];
        if ( !empty($this->DuplicityFilters) ) {
            foreach ( $this->DuplicityFilters as $filter ) {
                $array[] = [
                    'mode' => $filter['mode'],
                    'path' => $filter['path']
                ];
            }
        }
        return $array;
    }

    public function setAuthLocations(array $auth_locations, bool $hashed=false): self
    {
        if ( !empty($auth_locations) ) {
            foreach ( $auth_locations as $index => $location ) {

                if ( !empty($location['password']) && $hashed === false) {
                    $auth_locations[$index]['password'] = $this->generateAuthLocationHash($location['password']);
                }

                if ( empty($location['id']) ) {
                    $auth_locations[$index]['id'] = $this->generateAuthLocationId();
                } else {
                    $savedLocation = $this->findLocationById($location['id']);
                    if ( !empty($savedLocation) && empty($location['password']) ) {
                        $auth_locations[$index]['password'] = $savedLocation['password'];
                    }
                }

            }
        }
        $this->auth_locations = $auth_locations;

        return $this;
    }

    private function findLocationById($id): array
    {
        foreach ($this->auth_locations as $location) {
            if ( $location['id'] === $id ) {
                return $location;
            }
        }

        return [];
    }

    private function generateAuthLocationHash($password): string
    {
        $salt = str_replace('+', '.', base64_encode(random_bytes(6)));
        return crypt($password, '$6$'.$salt.'$');
    }

    private function generateAuthLocationId(): string
    {
        return uniqid('', true);
    }

    public function getNginxTemplate(): ?NginxTemplate
    {
        return $this->nginx_template;
    }

    public function setNginxTemplate(?NginxTemplate $nginx_template): self
    {
        $this->nginx_template = $nginx_template;

        return $this;
    }

    public function getNginxBlock(): ?string
    {
        return $this->nginx_block;
    }

    public function setNginxBlock(?string $nginx_block): self
    {
        $this->nginx_block = $nginx_block;

        return $this;
    }

    public function getActive(): ?bool
    {
        return $this->active;
    }

    public function setActive(?bool $active): self
    {
        $this->active = $active;

        return $this;
    }

    public function getVolume(): ?int
    {
        return $this->volume;
    }

    public function setVolume(?int $volume): self
    {
        $this->volume = $volume;

        return $this;
    }

    /**
     * @return Collection|Ftp[]
     */
    public function getFtps(): Collection
    {
        return $this->ftps;
    }

    public function addFtp(Ftp $ftp): self
    {
        if (!$this->ftps->contains($ftp)) {
            $this->ftps[] = $ftp;
            $ftp->setProject($this);
        }

        return $this;
    }

    public function removeFtp(Ftp $ftp): self
    {
        if ($this->ftps->removeElement($ftp)) {
            // set the owning side to null (unless already changed)
            if ($ftp->getProject() === $this) {
                $ftp->setProject(null);
            }
        }

        return $this;
    }

    public function getDuplicityFilters(): ?array
    {
        return $this->DuplicityFilters;
    }

    public function setDuplicityFilters(?array $DuplicityFilters): self
    {
        $this->DuplicityFilters = $DuplicityFilters;

        return $this;
    }

}
