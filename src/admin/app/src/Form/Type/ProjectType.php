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
use Symfony\Component\Validator\Constraints\Regex;
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
            'label' => 'form.label.uid',
            'row_attr' => ['class' => 'form-group uid-row'],
            'help' => 'form.help.uid',
        ])
        ->add('name', TextType::class, [
            'label' => 'form.label.name',
            'constraints' => [
                new NotBlank(),
                new Regex([
                    'pattern' => '/^[a-z][a-z0-9]*$/',
                    'message' => 'form.name_regex',
                ]),
            ],
            'help' => 'form.help.project_name',
            'attr' => ['placeholder' => 'e.g. myproject'],
        ])
        ->add('password', PasswordType::class, [
            'always_empty' => true,
            'required' => false,
            'empty_data' => '',
            'label' => 'form.label.password',
            'help' => 'form.help.password',
        ])
        ->add('domains', DomainsType::class, [
            'entry_type' => DomainType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'constraints' => new NotBlank(),
            'prototype' => true,
            'label' => 'form.label.domains',
            'help' => 'form.help.project_domains',
        ])
        ->add('volume', ChoiceType::class, [
            'choices' => range(0, count($this->projects_volumes)-1),
            'choice_label' => function ($choice, $key, $value) {
                return $this->projects_volumes[$key];
            },
            'label' => 'form.label.volume',
            'help' => 'form.help.volume',
        ])
        ->add('https', EntityType::class, [
            'class' => HttpsType::class,
            'choice_label' => function ($httpsType) {
                return $httpsType->getName();
            },
            'expanded' => false,
            'label' => 'form.label.https',
            'help' => 'form.help.project_https',
        ])
        ->add('nginx_template', EntityType::class, [
            'class' => NginxTemplate::class,
            'choice_label' => function ($template) {
                return $template->getLabel();
            },
            'expanded' => false,
            'label' => 'form.label.nginx_template',
            'help' => 'form.help.nginx_template',
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
            'expanded' => false,
            'label' => 'form.label.backend',
            'help' => 'form.help.backend',
        ])
        ->add('redirect', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.redirect',
            'help' => 'form.help.redirect',
        ])
        ->add('gzip', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.gzip',
            'help' => 'form.help.gzip',
        ])
        ->add('nginx_options', NginxOptionsType::class, [
            'entry_type' => NginxOptionType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'by_reference' => false,
            'prototype' => true,
            'label' => 'form.label.nginx_options',
            'help' => 'form.help.nginx_options',
        ])
        ->add('nginx_block', TextareaType::class, [
            'required' => false,
            'label' => 'form.label.nginx_block',
            'help' => 'form.help.nginx_block',
        ])
        ->add('auth_locations', AuthLocationsType::class, [
            'entry_type' => AuthLocationType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'by_reference' => false,
            'prototype' => true,
            'label' => 'form.label.auth_locations',
            'help' => 'form.help.auth_locations',
        ])
        ->add('backup', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.backup',
            'help' => 'form.help.backup',
        ])
        ->add('DuplicityFilters', DuplicityFiltersType::class, [
            'entry_type' => DuplicityFilterType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'prototype' => true,
            'label' => 'form.label.DuplicityFilters',
            'help' => 'form.help.DuplicityFilters',
        ])
        ->add('Memcached', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.Memcached',
            'help' => 'form.help.Memcached',
        ])
        ->add('Solr', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.Solr',
            'help' => 'form.help.Solr',
        ])
        ->add('Elastic', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.Elastic',
            'help' => 'form.help.Elastic',
        ])
        ->add('mysql', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.mysql',
            'help' => 'form.help.mysql',
        ])
        ->add('mysql5', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.mysql5',
            'help' => 'form.help.mysql5',
        ])
        ->add('postgre', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.postgre',
            'help' => 'form.help.postgre',
        ])
        ->add('root_folder', TextType::class, [
            'constraints' => new NotBlank(),
            'label' => 'form.label.root_folder',
            'help' => 'form.help.root_folder',
            'attr' => ['placeholder' => 'e.g. public'],
        ])
        ->add('gunicorn_app_module', TextType::class, [
            'required' => false,
            'label' => 'form.label.gunicorn_app_module',
            'help' => 'form.help.gunicorn_app_module',
            'attr' => ['placeholder' => 'e.g. app:application'],
        ])
        ->add('active', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.active',
            'help' => 'form.help.project_active',
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
