# odoo-sample-report-py3o

Utilizando o py3o na versão 8.0 c/ buildout
===========================================

Exemplo de arquivo de configuração
```
[buildout]

parts =
    odoo

[odoo]
recipe = anybox.recipe.odoo:server
version = git https://github.com/odoo/odoo.git odoo 8.0 depth=1

addons =
    hg ssh://hg@bitbucket.org/xcg/report_py3o report_py3o odoo8 group=reports
    git git@github.com:kmee/odoo-sample-report-py3o.git sample-py3o 8.0

options.admin_passwd = admin

eggs =
    py3o.template


```
