<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\HiddenType;

class AuthLocationIdType extends AbstractType
{
    public function getParent(): string
    {
        return HiddenType::class;
    }
}
