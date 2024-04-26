# Barky Refactor 3

The [OODA Loop](https://en.wikipedia.org/wiki/OODA_loop) was created by John Boyd and is a perfect metaphor to understand event-driven development (EVD).

<img src="../../docs/img/2880px-OODA.Boyd.svg.png" width=600px>

In EVD the program loops and waits to detect a known event, evaluates that event, and then acts.  Django itself works with the HTTP webserver using the WSGI standard to participate in that server's event loop.  However, we can develop an event loop within the app.

As usual, we'll look for ways to simplify our approach and **NOT** fight Django.

For this reason, we'll consider Celery.

## P&G: Is This Like Celery?

P&G say this about the matter:

> Celery is a popular tool in the Python world for deferring self-contained chunks of work to an asynchronous task queue. The message bus we’re presenting here is very different, so the short answer to the above question is no; our message bus has more in common with an Express.js app, a UI event loop, or an actor framework.

> If you do have a requirement for moving work off the main thread, you can still use our event-based metaphors, but we suggest you use external events for that. There’s more discussion in chapter 11, but essentially, if you implement a way of persisting events to a centralized store, you can subscribe other containers or other microservices to them. Then that same concept of using events to separate responsibilities across units of work within a single process/service can be extended across multiple processes—​which may be different containers within the same service, or totally different microservices.

> If you follow us in this approach, your API for distributing tasks is your event classes—or a JSON representation of them. This allows you a lot of flexibility in who you distribute tasks to; they need not necessarily be Python services. Celery’s API for distributing tasks is essentially "function name plus arguments," which is more restrictive, and Python-only.

As much as I accept this wisdom, we've become used to taking the "easier" path and accepting the monolith.

## Celery and Django

Tools like Celery and Redis are mostly unfriendly to a windows development environment.  One way around this is containerization, which I have largely eschewed here.  So, we'll muddle through as there are ways around this.

Let's be clear though, in order to do Celery, we'll want to establish what we'll exactly accomplish with Celery:

1. Celery Basics (P&G Chapters 8 and 9 )
   1. Celery 5.x is not supposed to work on Windows, but we'll be okay-ish. Bjoern Stiel has some information that is fairly recent: [Celery on Windows: What's the latest?](https://celery.school/celery-on-windows)
1. Using Redis as a message broker
   1. [Windows instructions](https://developer.redis.com/create/windows/) - will require admin rights.

## Celery Alternative - Huey and Django

While [Huey](https://github.com/coleifer/huey) doesn't avoid redis, it does present a slightly simpler, and windows-friendly, alternative

## Key Producer/Consumer Demo

[producer-consumer](https://github.com/arsenmakovei/producer-consumer)

## Other options

- Channels
- Signals

## The Django Signals Option

From the Django documentation:

> Django includes a “signal dispatcher” which helps decoupled applications get notified when actions occur elsewhere in the framework. In a nutshell, signals allow certain senders to notify a set of receivers that some action has taken place. They’re especially useful when many pieces of code may be interested in the same events.

This will handily accommodate the premise of the internal message bus (from P&G):

> The Message Bus Maps Events to Handlers: A message bus basically says, "When I see this event, I should invoke the following handler function." In other words, it’s a simple publish-subscribe system. Handlers are subscribed to receive events, which we publish to the bus.

Django Signals does what P&G describe and, as we have opted for the monolith, then we'll just go the Django Signals route.

Django Signals provides a relatively limited built-in vocabulary for known events, but the provided set of signals cover a majority of use cases.  The built-in signals (a signal is our event) include the following categories:
- [Model Signals](https://docs.djangoproject.com/en/5.0/ref/signals/#module-django.db.models.signals)
- [Management Signals](https://docs.djangoproject.com/en/5.0/ref/signals/#management-signals)
- [Request/Response Signals](https://docs.djangoproject.com/en/5.0/ref/signals/#module-django.core.signals)
- [Test Signals](https://docs.djangoproject.com/en/5.0/ref/signals/#module-django.test.signals)

If those built-in signals do not work for us, we can also [define any custom signal](https://docs.djangoproject.com/en/5.0/topics/signals/#defining-and-sending-signals).

## New to Refactor 3

- For simplicity, I'll be using Django Signals rather than Celery.
- As we are moving entirely into the Django monolith, remove the editable package: `pip uninstall barky`

## Barky Refactoring Roadmap

Dane Hillard's code focused on a command-line interface, but we will systematically refactor that code, across a series of branches, to do the following:

1. Replace the custom data handling (the DatabaseManager module) with the [Django O/RM](https://docs.djangoproject.com/en/5.0/topics/db/queries/)
   1. Replace the existing DatabaseManager with the Django ORM.
   1. Replace the CLI web-based REST API using the Django REST Framework.
   1. SOLID
   1. Use [DRF's testing facilities](https://www.django-rest-framework.org/api-guide/testing/#api-test-cases)
1. Adopt the suggestions from Percival and Gregory regarding the Unit of Work and Respository Pattern and Django: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
   1. Add a separate Domain Model and explore the pros and cons of this: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
1. Introduce messaging using Celery with Django. This will serve as a message bus to augment event-driven architecture.
   1. [Django is well supported using Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) as an asynchronous message/task queue.
   1. Reintroduce the [Command pattern](https://refactoring.guru/design-patterns/command) as a means to encapsule the transactional intent of messages passed within Celery.
1. Improve architecture:
   1. [CQRS in general](https://douwevandermeij.medium.com/the-repository-pattern-via-cqrs-with-python-django-elasticsearch-cb38437721d3) and in [Django](https://django-cqrs.readthedocs.io/en/latest/)
   1. Dependency injection - [A good overview](https://thinhdanggroup.github.io/python-dependency-injection/), [DI with specific Flask and Django examples](https://snyk.io/blog/dependency-injection-python/), and a [Comprehensive Python Dependency Injection Framework](https://python-dependency-injector.ets-labs.org/)

## Refactor to Assignments Map

1. Refactor 1 (DRF and ORM): Assignment 5
1. Refactor 2 (Repository Pattern and UoW ): Assignment 6
1. Refactor 3 (Django Signals and the Return of the Command): Assignment 7
1. Refactor 4 (Django Channels to approximate CQRS and DI/Bootstrapping): Assignment 8
