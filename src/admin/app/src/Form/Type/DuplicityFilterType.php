<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CollectionType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use App\Form\Type\AuthLocationPathType;

class DuplicityFilterType extends AbstractType
{

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('mode', DuplicityFilterModeType::class, [
            'choices' => [
                'exclude' => 'exclude',
                'include' => 'include'
            ],
            'expanded' => false,
            'multiple' => false
        ])
        ->add('path', DuplicityFilterPathType::class, [
            'constraints' => new NotBlank(),
        ])
        ;
    }

}
