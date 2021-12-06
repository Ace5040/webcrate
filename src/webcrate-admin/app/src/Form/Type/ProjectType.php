<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use App\Entity\Project;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

use App\Entity\HttpsType;
use App\Entity\Backend;
use App\Entity\NginxTemplate;
use App\Repository\BackendRepository;

use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\PasswordType;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\TextareaType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use App\Form\Type\DuplicityFiltersType;
use App\Form\Type\DuplicityFilterType;
use App\Form\Type\DomainsType;
use App\Form\Type\DomainType;
use App\Form\Type\NginxOptionsType;
use App\Form\Type\NginxOptionType;
use App\Form\Type\AuthLocationsType;
use App\Form\Type\AuthLocationType;
use App\Form\Type\FtpsType;
use App\Form\Type\FtpType;
use Symfony\Component\DependencyInjection\ParameterBag\ParameterBagInterface;

class ProjectType extends AbstractType
{
    /**
     * @var array
     */
    private $projects_volumes;

    public function __construct(ParameterBagInterface $params)
    {
        $this->projects_volumes = explode(':', $params->get('projects_volumes'));
    }

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('uid', TextType::class, [
            'disabled' => true,
        ])
        ->add('name', TextType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('password', PasswordType::class, [
            'always_empty' => true,
            'required' => false,
            'empty_data' => '',
        ])
        ->add('domains', DomainsType::class, [
            'entry_type' => DomainType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'constraints' => new NotBlank(),
            'prototype' => true,
        ])
        ->add('ftps', FtpsType::class, [
            'entry_type' => FtpType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'constraints' => new NotBlank(),
            'prototype' => true,
        ])
        ->add('volume', ChoiceType::class, [
            'choices' => range(0, count($this->projects_volumes)-1),
            'choice_label' => function ($choice, $key, $value) {
                return $this->projects_volumes[$key];
            }
        ])
        ->add('https', EntityType::class, [
            'class' => HttpsType::class,
            'choice_label' => function ($httpsType) {
                return $httpsType->getName();
            },
            'expanded' => false
        ])
        ->add('nginx_template', EntityType::class, [
            'class' => NginxTemplate::class,
            'choice_label' => function ($template) {
                return $template->getLabel();
            },
            'expanded' => false
        ])
        ->add('backend', EntityType::class, [
            'class' => Backend::class,
            'choice_label' => function ($backend) {
                return $backend->getFullName();
            },
            'query_builder' => function (BackendRepository $er) {
                return $er->createQueryBuilder('b')
                    ->addOrderBy('b.name', 'ASC')
                    ->addOrderBy('b.version', 'DESC');
            },
            'expanded' => false
        ])
        ->add('redirect', CheckboxType::class, [
            'required' => false,
        ])
        ->add('gzip', CheckboxType::class, [
            'required' => false,
        ])
        ->add('nginx_options', NginxOptionsType::class, [
            'entry_type' => NginxOptionType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'by_reference' => false,
            'prototype' => true,
        ])
        ->add('nginx_block', TextareaType::class, [
            'required' => false,
        ])
        ->add('auth_locations', AuthLocationsType::class, [
            'entry_type' => AuthLocationType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'by_reference' => false,
            'prototype' => true,
        ])
        ->add('backup', CheckboxType::class, [
            'required' => false,
        ])
        ->add('DuplicityFilters', DuplicityFiltersType::class, [
            'entry_type' => DuplicityFilterType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'prototype' => true,
        ])
        ->add('Memcached', CheckboxType::class, [
            'required' => false,
        ])
        ->add('Solr', CheckboxType::class, [
            'required' => false,
        ])
        ->add('mysql', CheckboxType::class, [
            'required' => false,
        ])
        ->add('mysql5', CheckboxType::class, [
            'required' => false,
        ])
        ->add('postgre', CheckboxType::class, [
            'required' => false,
        ])
        ->add('root_folder', TextType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('gunicorn_app_module', TextType::class, [
            'required' => false,
        ])
        ->add('active', CheckboxType::class, [
            'required' => false,
        ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Project::class,
        ]);
    }

}
