<?php

namespace App\EventSubscriber;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;

class LocaleSubscriber implements EventSubscriberInterface
{
    private string $defaultLocale;

    public function __construct(string $defaultLocale = 'en')
    {
        $this->defaultLocale = $defaultLocale;
    }

    public function onKernelRequest(RequestEvent $event): void
    {
        $request = $event->getRequest();
        $locale = $request->cookies->get('app_locale', $this->defaultLocale);
        if (in_array($locale, ['en', 'ru', 'zh'], true)) {
            $request->setLocale($locale);
        }
    }

    public static function getSubscribedEvents(): array
    {
        // Priority 15: after LocaleListener (16), before TranslatorListener (10)
        return [
            KernelEvents::REQUEST => [['onKernelRequest', 15]],
        ];
    }
}
