<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CollectionType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use App\Form\Type\AuthLocationPathType;
use App\Form\Type\AuthLocationTitleType;
use App\Form\Type\AuthLocationUserType;
use App\Form\Type\AuthLocationPasswordType;
use App\Form\Type\AuthLocationIdType;

class AuthLocationType extends AbstractType
{

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('id', AuthLocationIdType::class, [
        ])
        ->add('path', AuthLocationPathType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('title', AuthLocationTitleType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('user', AuthLocationUserType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('password', AuthLocationPasswordType::class, [
            'always_empty' => true,
            'required' => false,
            'empty_data' => '',
        ])
        ;
    }

}
