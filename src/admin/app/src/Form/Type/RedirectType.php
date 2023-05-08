<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use App\Entity\Redirect;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

use App\Entity\HttpsType;

use Symfony\Component\Validator\Constraints\NotBlank;
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
            'constraints' => new NotBlank(),
        ])
        ->add('domains', DomainsType::class, [
            'entry_type' => DomainType::class,
            'allow_add' => true,
            'allow_delete' => true,
            'delete_empty' => true,
            'constraints' => new NotBlank(),
            'prototype' => true,
        ])
        ->add('https', EntityType::class, [
            'class' => HttpsType::class,
            'choice_label' => function ($httpsType) {
                return $httpsType->getName();
            },
            'expanded' => false
        ])
        ->add('url', TextType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('active', CheckboxType::class, [
            'required' => false,
        ]);
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Redirect::class,
        ]);
    }

}
