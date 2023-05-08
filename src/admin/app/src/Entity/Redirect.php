<?php

namespace App\Entity;

use App\Repository\RedirectRepository;
use Symfony\Component\Yaml\Yaml;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=RedirectRepository::class)
 */
class Redirect
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
     * @ORM\Column(type="array")
     */
    private $domains = [];

    /**
     * @ORM\Column(type="boolean")
     */
    private $active;

    /**
     * @ORM\Column(type="string", length=255)
     */
    private $url;

    /**
     * @ORM\ManyToOne(targetEntity=HttpsType::class)
     * @ORM\JoinColumn(nullable=false)
     */
    private $https;

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

    public function getDomains(): ?array
    {
        return $this->domains;
    }

    public function setDomains(array $domains): self
    {
        $this->domains = $domains;

        return $this;
    }

    public function getActive(): ?bool
    {
        return $this->active;
    }

    public function setActive(bool $active): self
    {
        $this->active = $active;

        return $this;
    }

    public function getUrl(): ?string
    {
        return $this->url;
    }

    public function setUrl(string $url): self
    {
        $this->url = $url;

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

    public function getActualSha256Sum()
    {
        $redirectName = $this->getName();
        $path = "/webcrate/meta/redirect-$redirectName.checksum";
        if ( file_exists($path) ) {
            return file_get_contents($path);
        } else {
            return '';
        }
    }

    public function getSha256Sum()
    {
        $ymlData = $this->getYmlData();
        return hash('sha256', $ymlData);
    }

    public function getYmlData()
    {
        $yamlData = Yaml::dump($this->toObject(), 3, 2, Yaml::DUMP_OBJECT_AS_MAP);
        $yamlData = json_encode($this->toObject(), JSON_UNESCAPED_SLASHES);
        $redirectName = $this->getName();
        $path = "/webcrate/meta/redirect-$redirectName.ymldata";
        file_put_contents($path, $yamlData);
        return $yamlData;
    }

    public function isActual()
    {
        return $this->getSha256Sum() === $this->getActualSha256Sum();
    }

    public function toObject(): object
    {
        return  (object)[
            'active' => $this->getActive(),
            'domains' => $this->domains,
            'url' => $this->url,
            'https' => !empty($this->https) ? $this->https->getName() : 'disabled',
        ];
    }

}
