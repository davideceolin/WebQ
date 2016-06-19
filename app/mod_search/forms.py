# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, HiddenField, RadioField, SubmitField, SelectMultipleField, widgets# BooleanField

# Import Form validators
from wtforms.validators import Required #, Email, EqualTo

class MultiCheckboxField(SelectMultipleField):
    """
        A multiple-select, except displays a list of checkboxes.
        
        Iterating the field will produce subfields, allowing custom rendering of
        the enclosed checkbox fields.
        """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Define the login form (WTForms)
class SearchForm(Form):
    s = TextField('s',[Required()])
    search = SubmitField('search')

class QualityForm(Form):
    #target = HiddenField('target')
    overallQuality = RadioField('overallQuality', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    accuracy = RadioField('accuracy', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    completeness = RadioField('completeness', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    neutrality = RadioField('neutrality', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    relevance = RadioField('relevance', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    trustworthiness = RadioField('trustworthiness', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    readability = RadioField('readability', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    precision = RadioField('precision', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    remarks = TextField('remarks')
    submit = SubmitField('submit')

class BestForm(Form):
    articles =  MultiCheckboxField("Docs", coerce=int)