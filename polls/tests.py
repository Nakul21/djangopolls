from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        This test case tests if the published date is a future date, then it should return
        false for future questions

        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        This test case tests if the published date is an old date, then it should return
        false for old questions

        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently(self):
        """
        This test case tests if the published date is a recent one, then it should return
        True for recent questions older than a day

        """
        time = timezone.now() - datetime.timedelta(hours=23 , minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    This method creates a question with the given attributes of a model (question_text
    and pub_date)

    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):

    def test_no_questions_exist(self):
        """
        This method tests if there are any questions present in our database, if there is no
        question in the database it asserts an appropriate message saying the "polls app doesn't
        contain no questions"
        """

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_questions_list'], [])

    def test_past_question(self):
        """
        This method tests if the question that is created specifically has the published date
        of the past, it that's the case then all the questions with the past published date of more than
        30 days is displayed

        """
        question = create_question(question_text='Past Question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [question])

    def test_future_question1(self):
        """
        This method tests the published date of the created question by creating a question
        and givong the newly created question date as future date, this question won't be displayed in the
        question list as polls app only displays questions whose published date is either past date or
        present date.

        """
        create_question(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_questions_list'], [])

    def test_future_and_past_question(self):
        """
        This method tests the published date of the created question by creating a question
        with future and past date, this question will only display past question
        (question_text='Past Question') as polls app only displays questions whose published
        date is either past date or present date.

        """
        question = create_question(question_text='Past Question', days=-30)
        create_question(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [question])

    def test_two_past_questions(self):
        """

        """
        question1 = create_question(question_text='Past Question1', days=-30)
        question2 = create_question(question_text='Past Question2', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [question2, question1],)

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """

        """
        future_question = create_question(question_text='Future Question', days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """

        """
        past_question = create_question(question_text='Past Question', days=-30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)