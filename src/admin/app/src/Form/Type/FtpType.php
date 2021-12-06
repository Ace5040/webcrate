<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CollectionType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\HiddenType;
use App\Form\Type\FtpNameType;
use App\Form\Type\FtpPasswordType;
use App\Form\Type\FtpType;
use App\Entity\Ftp;

class FtpType extends AbstractType
{

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
        ->add('weight', HiddenType::class, [
        ])
        ->add('name', FtpNameType::class, [
            'constraints' => new NotBlank(),
        ])
        ->add('password', FtpPasswordType::class, [
            'always_empty' => true,
            'required' => false,
            'empty_data' => '',
        ])
        ->add('home', FtpHomeType::class, [
        ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            'data_class' => Ftp::class
        ]);
    }

}
