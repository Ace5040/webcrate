<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use App\Entity\Redirect;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

use App\Entity\HttpsType;

use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Validator\Constraints\Regex;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use App\Form\Type\DomainsType;
use App\Form\Type\DomainType;

class RedirectType extends AbstractType
{

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('name', TextType::class, [
            'label' => 'form.label.name',
            'constraints' => [
                new NotBlank(),
                new Regex([
                    'pattern' => '/^[a-z][a-z0-9]*$/',
                    'message' => 'form.name_regex',
                ]),
            ],
            'help' => 'form.help.redirect_name',
            'attr' => ['placeholder' => 'e.g. myredirect'],
        ])
        ->add('domains', DomainsType::class, [
            'entry_type' => DomainType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'constraints' => new NotBlank(),
            'prototype' => true,
            'label' => 'form.label.domains',
            'help' => 'form.help.redirect_domains',
        ])
        ->add('https', EntityType::class, [
            'class' => HttpsType::class,
            'choice_label' => function ($httpsType) {
                return $httpsType->getName();
            },
            'expanded' => false,
            'label' => 'form.label.https',
            'help' => 'form.help.redirect_https',
        ])
        ->add('url', TextType::class, [
            'constraints' => new NotBlank(),
            'label' => 'form.label.url',
            'help' => 'form.help.url',
            'attr' => ['placeholder' => 'e.g. https://example.com'],
        ])
        ->add('active', CheckboxType::class, [
            'required' => false,
            'label' => 'form.label.active',
            'help' => 'form.help.redirect_active',
        ]);
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Redirect::class,
        ]);
    }

}
