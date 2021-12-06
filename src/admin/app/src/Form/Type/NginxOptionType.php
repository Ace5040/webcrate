<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CollectionType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use App\Entity\NginxOption;
use App\Form\Type\NginxOptionNameType;
use App\Form\Type\NginxOptionValueType;

class NginxOptionType extends AbstractType
{

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('name', NginxOptionNameType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('value', NginxOptionValueType::class, [
            'constraints' => new NotBlank(),
        ])
        ;
    }

}
