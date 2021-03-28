<?php

namespace App\Form\Type;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;

class DuplicityFilterModeType extends AbstractType
{
    public function getParent(): string
    {
        return ChoiceType::class;
    }
}
