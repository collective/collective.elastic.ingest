# -*- coding: utf-8 -*-
from . import postprocessing


# ------------------------------------------------------------------------------
# postprocessors


def test_extract_binary__richtext():
    return
    content = {
        # skip fields
        "text": {
            "content-type": "text/html",
            "data": '<div class="hero">\n<h1>Welcome!</h1>\n<p><a class="context" href="https://plone.org/" rel="noopener" target="_blank">Learn more about Plone</a></p>\n</div>\n<p class="discreet">If you\'re seeing this instead of the web site you were expecting, the owner of this web site has just installed Plone. Do not contact the Plone Team or the Plone support channels about this.</p>\n<h2>Get started</h2>\n<p>Before you start exploring your newly created Plone site, please do the following:</p>\n<ol>\n<li>Make sure you are logged in as an admin/manager user. <span class="discreet">(You should have a Site Setup entry in the user menu)</span></li>\n<li><a href="http://localhost:8080/Plone/@@mail-controlpanel" rel="noopener" target="_blank">Set up your mail server</a>. <span class="discreet">(Plone needs a valid SMTP server to verify users and send out password reminders)</span></li>\n<li><a href="http://localhost:8080/Plone/@@security-controlpanel" rel="noopener" target="_blank">Decide what security level you want on your site</a>. <span class="discreet">(Allow self registration, password policies, etc)</span></li>\n</ol>\n<h2>Get comfortable</h2>\n<p>After that, we suggest you do one or more of the following:</p>\n<ul>\n<li>Find out <a class="link-plain" href="http://plone.com/features/" rel="noopener" target="_blank">What\'s new in Plone</a>.</li>\n<li>Read the <a class="link-plain" href="http://docs.plone.org" rel="noopener" target="_blank">documentation</a>.</li>\n<li>Follow a <a class="link-plain" href="https://training.plone.org" rel="noopener" target="_blank">training</a>.</li>\n<li>Explore the <a class="link-plain" href="https://plone.org/download/add-ons" rel="noopener" target="_blank">available add-ons</a> for Plone.</li>\n<li>Read and/or subscribe to the <a class="link-plain" href="http://plone.org/support" rel="noopener" target="_blank">support channels</a>.</li>\n<li>Find out <a class="link-plain" href="http://plone.com/success-stories" rel="noopener" target="_blank">how others are using Plone</a>.</li>\n</ul>\n<h2>Make it your own</h2>\n<p>Plone has a lot of different settings that can be used to make it do what you want it to. Some examples:</p>\n<ul>\n<li>Try out a different theme, either pick from <a href="http://localhost:8080/Plone/@@theming-controlpanel" rel="noopener" target="_blank">the included ones</a>, or one of the <a class="link-plain" href="http://plone.org/products/" rel="noopener" target="_blank">available themes from plone.org</a>. <span class="discreet">(Make sure the theme is compatible with the version of Plone you are currently using)</span></li>\n<li><a href="http://localhost:8080/Plone/@@content-controlpanel" rel="noopener" target="_blank"> Decide what kind of workflow you want in your site.</a> <span class="discreet">(The default is typical for a public web site; if you want to use Plone as a closed intranet or extranet, you can choose a different workflow.)</span></li>\n<li>By default, Plone uses a visual editor for content. <span class="discreet">(If you prefer text-based syntax and/or wiki syntax, you can change this in the <a href="http://localhost:8080/Plone/@@markup-controlpanel" rel="noopener" target="_blank">markup control panel</a>)</span></li>\n<li>…and many more settings are available in the <a href="http://localhost:8080/Plone/@@overview-controlpanel" rel="noopener" target="_blank">Site Setup</a>.</li>\n</ul>\n<h2>Tell us how you use it</h2>\n<p>Are you doing something interesting with Plone? Big site deployments, interesting use cases? Do you have a company that delivers Plone-based solutions?</p>\n<ul>\n<li>Add your company as a <a class="link-plain" href="http://plone.com/providers" rel="noopener" target="_blank">Plone provider</a>.</li>\n<li>Add a <a class="link-plain" href="http://plone.com/success-stories" rel="noopener" target="_blank">success story</a> describing your deployed project and customer.</li>\n</ul>\n<h2>Find out more about Plone</h2>\n<p>Plone is a powerful content management system built on a rock-solid application stack written using the Python programming language. More about these technologies:</p>\n<ul>\n<li>The <a class="link-plain" href="http://plone.com" rel="noopener" target="_blank">Plone open source Content Management System</a> web site for evaluators and decision makers.</li>\n<li>The <a class="link-plain" href="http://plone.org" rel="noopener" target="_blank">Plone community </a> web site for developers.</li>\n<li>The <a class="link-plain" href="http://www.python.org" rel="noopener" target="_blank">Python programming language</a> web site.</li>\n</ul>\n<h2>Support the Plone Foundation</h2>\n<p>Plone is made possible only through the efforts of thousands of dedicated individuals and hundreds of companies. The Plone Foundation:</p>\n<ul>\n<li>…protects and promotes Plone.</li>\n<li>…is a registered 501(c)(3) charitable organization.</li>\n<li>…donations are tax-deductible.</li>\n<li><a href="https://plone.org/sponsors/be-a-hero" rel="noopener" target="_blank">Support the Foundation and help make Plone better!</a></li>\n</ul>\n<p>Thanks for using our product; we hope you like it!</p>\n<p>—The Plone Team</p>',  # noqa: 501
            "encoding": "utf-8",
        },
        # skip fields
    }

    postprocessing._extract_binary(content, {"expansion_fields": {}}, "extract")
    assert content == {"keep_me": "Bumblebee"}


example_image = {
    "@components": {
        #  skip details here for test
    },
    # skip fields
    "image": {
        "content-type": "image/png",
        "download": "http://localhost:8080/Plone/plone-icon-16.png/@@images/62286803-480e-4fc4-963c-cd834285565a.png",  # noqa: 501
        "filename": "plone-icon-16.png",
        "height": 16,
        "scales": {
            "icon": {
                "download": "http://localhost:8080/Plone/plone-icon-16.png/@@images/86e77719-2ff6-4c7a-90ea-50b6565dea63.png",  # noqa: 501
                "height": 16,
                "width": 16,
            },
            # skip other scales
        },
        "size": 2963,
        "width": 16,
    },
    # skip fields
}

example_image = {
    "@components": {
        #  skip details here for test
    },
    # skip fields
    "file": {
        "content-type": "image/png",
        "download": "http://localhost:8080/Plone/plone-icon-16-1.png/@@download/file",
        "filename": "plone-icon-16.png",
        "size": 2963,
    },
    # skip fields
}


# ------------------------------------------------------------------------------
# full processor
