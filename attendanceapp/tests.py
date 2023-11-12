from django.test import TestCase
from attendanceapp.models import Attendance
from django.urls import reverse, resolve
from .views import AttendanceList, AddItem, EditItem, DeleteItem, RegisterAccount
from django.contrib.auth.views import LoginView, LogoutView


# modelのテスト
class TestModels(TestCase):
    # 初期状態では何も登録されていないことのテスト
    def test_is_empty(self):
        saved_posts = Attendance.objects.all()
        self.assertEqual(saved_posts.count(), 0)

    # 登録したレコード数と格納されたレコード数が同じかテスト
    def test_is_count_one(self):
        post = Attendance(hour=20, minute=20, state='開始')
        post.save()
        saved_posts = Attendance.objects.all()
        self.assertEqual(saved_posts.count(), 1)

    # 保存した値と格納された値が同じかテスト
    def test_saving_and_retrieving_post(self):
        hour = 10
        minute = 20
        state = '開始'
        post = Attendance(hour=hour, minute=minute, state=state)
        post.save()
        saved_posts = Attendance.objects.all()
        self.assertEqual(hour, saved_posts[0].hour)
        self.assertEqual(minute, saved_posts[0].minute)
        self.assertEqual(state, saved_posts[0].state)


# urlのテスト
class TestUrls(TestCase):
    # 全ページへのurlでのアクセステスト
    def test_all_urls(self):
        urls = ['/add-item/', '/login/', '/logout/', '/register/',
                '/edit-item/0', '/delete-item/0', '/']
        views = [AddItem, LoginView, LogoutView, RegisterAccount,
                 EditItem, DeleteItem, AttendanceList]
        for url, view in zip(urls, views):
            view_per_url = resolve(url)
            self.assertEqual(view_per_url.func.view_class, view)


# viewのテスト
class TestViewsBeforeSignup(TestCase):
    # ユーザー登録前にアクセス可能なページへアクセスし、ステータスコードを確認
    def test_get(self):
        path_names = ['register', 'login']
        for path_name in path_names:
            response = self.client.get(reverse(path_name))
            self.assertEqual(response.status_code, 200)
        # top画面は、ログイン画面へリダイレクトされる
        path_names = ['top']
        for path_name in path_names:
            response = self.client.get(reverse(path_name))
            self.assertEqual(response.status_code, 302)


class TestViewsAfterSignup(TestCase):
    # 実際にデータを登録
    def setUp(self):
        # アカウント登録
        _ = self.client.post(reverse('register'),
                             {'username': ' testuser',
                              'password1': 'fejgi1515Ca',
                              'password2': 'fejgi1515Ca'},
                             follow=True)
        # ログイン
        response = self.client.post(reverse('login'),
                                    {'username': 'testuser',
                                     'password': 'fejgi1515Ca'},
                                    follow=True)

        # データベース登録
        post1 = Attendance.objects.create(user=response.context['user'],
                                          hour=8, minute=40, state='開始')
        self.pk = post1.id
        _ = Attendance.objects.create(user=response.context['user'],
                                      hour=12, minute=0, state='停止')
        _ = Attendance.objects.create(user=response.context['user'],
                                      hour=13, minute=0, state='開始')
        _ = Attendance.objects.create(user=response.context['user'],
                                      hour=17, minute=40, state='終了')

    # ユーザー登録後にアクセス可能なページへアクセスし、ステータスコードを確認
    def test_get(self):
        # トップ画面と追加画面へのアクセステスト
        path_names = ['top', 'add-item', 'login']
        for path_name in path_names:
            response = self.client.get(reverse(path_name))
            self.assertEqual(response.status_code, 200)

        # 編集画面へのアクセステスト
        response = self.client.get(reverse('edit-item',
                                           kwargs={'pk': self.pk}))
        self.assertEqual(response.status_code, 200)

        # 削除画面へのアクセステスト
        response = self.client.get(reverse('delete-item',
                                           kwargs={'pk': self.pk}))
        self.assertEqual(response.status_code, 200)

    # 最終的な勤務時間が合うかどうかをテスト
    def test_workingtime(self):
        response = self.client.get(reverse('top'))
        self.assertEqual(response.context['message'], '本日の勤務時間は8時間00分です')

    # 削除画面でアイテムを消せるかをテスト
    def test_delete_item(self):
        saved_posts = Attendance.objects.all()
        item_length = saved_posts.count()
        _ = self.client.post(reverse('delete-item', kwargs={'pk': self.pk}))
        saved_posts = Attendance.objects.all()
        self.assertEqual(item_length-1, saved_posts.count())

    # 追加画面でアイテムを増やせるかをテスト
    def test_add_item(self):
        saved_posts = Attendance.objects.all()
        item_length = saved_posts.count()
        _ = self.client.post(reverse('add-item'),
                             {'hour': 15,
                              'minute': 0,
                              'state': '停止'},
                             follow=True)
        saved_posts = Attendance.objects.all()
        self.assertEqual(item_length+1, saved_posts.count())

    # 編集画面でアイテムの時間を変えられるかをテスト
    def test_edit_item(self):
        saved_posts = Attendance.objects.all()
        hour_before_edit = saved_posts[self.pk].hour
        _ = self.client.post(reverse('edit-item',
                                     kwargs={'pk': self.pk}),
                             {'hour': 15,
                              'minute': 0,
                              'state': '停止'},
                             follow=True)
        saved_posts = Attendance.objects.all()
        hour_after_edit = saved_posts[self.pk].hour
        self.assertNotEqual(hour_before_edit, hour_after_edit)
        response = self.client.get(reverse('top'))
        self.assertNotEqual(response.context['message'], '本日の勤務時間は8時間00分です')
