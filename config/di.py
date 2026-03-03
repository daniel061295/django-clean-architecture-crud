"""
Config Dependency Injection — Main injector configuration.

This module sets up the root injector for the application,
installing all bounded context modules.
"""
from injector import Injector

from store.di import StoreModule
from identity.di import IdentityModule
from billing.di import BillingModule


def create_injector() -> Injector:
    """
    Creates and configures the root application injector.
    
    Returns:
        Injector: Configured injector with all modules installed.
    """
    return Injector([
        StoreModule(),
        IdentityModule(),
        BillingModule(),
    ])
