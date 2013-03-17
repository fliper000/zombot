import vkutils
import mrutils

def Site(settings):
    if settings.getSite() == 'vk':
        return vkutils.VK(settings)
    else:
        return mrutils.MR(settings)
