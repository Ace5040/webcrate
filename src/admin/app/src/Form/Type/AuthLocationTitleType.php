<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\TextType;

class AuthLocationTitleType extends AbstractType
{
    public function getParent(): string
    {
        return TextType::class;
    }
}
