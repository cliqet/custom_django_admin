from uuid import uuid4

from django.core.cache import cache
from django.db import models


class BaseModel(models.Model):
    # NOTE: Use this for every model or if your model has another parent,
    # make sure that this is the base model
    # Override UID_PREFIX when you need to implement a uid field for the model.
    # Note that not every model that inherits from this needs to implement
    # a uid field and is optional. You can just go with django's default id
    # for some models where having a uid would not be necessary.
    UID_PREFIX = ''
    
    class Meta:
        abstract = True

    def generate_uid(self) -> str:
        return f'{self.UID_PREFIX}_{uuid4()}'
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Base queryset and model manager for models following the simple pattern
# of a model having a CACHE_KEY_PREFIX and invalidate cached value of 
# all the records of the model.
# Do not use this with models that relate to other models. Use only for 
# models where you want to cache the list of all its records and any update
# on one of the records invalidates the cache. If the model has related models
# in it, any update to that other model will not affect the cache and we do 
# not want that since we only want updated data and this means any field that 
# changes should invalidate the cache
class BaseCacheQuerySet(models.QuerySet):
    """
        Allow deleting of cache for specific model when deleting multiple 
        records from admin list view
    """
    def delete(self):
        # Iterate over each object in the queryset
        for obj in self:
            if cache.get(obj.CACHE_KEY_PREFIX):
                cache.delete(obj.CACHE_KEY_PREFIX)
                break
        
        return super().delete()
    

class BaseCacheManager(models.Manager):
    """
        This behaves the same as django default manager but is used for 
        model.objects so that multiple deletion of model records 
        will use the BaseCacheQuerySet to delete the cache
    """
    def get_queryset(self):
        return BaseCacheQuerySet(
            model=self.model, using=self._db, hints=self._hints
        )
    

class BaseCachedModel(BaseModel):
    """
        Use this model for those that barely change and has no related fields. 
        NOTE: Be careful when using with models that have related fields since 
        when those fields update, you may want to reflect the changes as well
        to what you have cached.
    """
    # Override this in models inheriting from this model
    CACHE_KEY_PREFIX = ''

    class Meta:
        abstract = True

    objects = BaseCacheManager()

    def save(self, *args, **kwargs):
        if cache.get(self.CACHE_KEY_PREFIX):
            cache.delete(self.CACHE_KEY_PREFIX)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if cache.get(self.CACHE_KEY_PREFIX):
            cache.delete(self.CACHE_KEY_PREFIX)

        super().delete(*args, **kwargs)


class HTMLField(models.TextField):
    """
        Use this for HTML fields to have WYSIWYG editing
    """




