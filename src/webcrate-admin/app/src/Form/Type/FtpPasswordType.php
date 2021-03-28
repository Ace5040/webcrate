<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\PasswordType;

class FtpPasswordType extends AbstractType
{
    public function getParent(): string
    {
        return PasswordType::class;
    }
}
