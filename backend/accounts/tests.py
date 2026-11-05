import re

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

PASSWORD = 'ClaveSegura123!'


def create_user(role, email=None):
    return User.objects.create_user(email=email or f'{role}@iglesia.test', password=PASSWORD, role=role)


class AuthenticationTests(APITestCase):
    def login(self, email, password=PASSWORD):
        return self.client.post(reverse('login'), {'email': email, 'password': password}, format='json')

    def test_public_registration_requires_approval(self):
        register = self.client.post(reverse('register'), {
            'email': 'coordinador@iglesia.test',
            'password': PASSWORD,
            'first_name': 'Ana',
        }, format='json')
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register.data['role'], User.Role.COORDINATOR)
        self.assertFalse(register.data['is_active'])
        self.assertEqual(self.login('coordinador@iglesia.test').status_code, status.HTTP_400_BAD_REQUEST)

        pending = User.objects.get(email='coordinador@iglesia.test')
        self.client.force_authenticate(create_user(User.Role.ADMINISTRATOR))
        approve = self.client.post(f'/api/users/{pending.pk}/approve/', {'role': User.Role.SECRETARY}, format='json')
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data['role'], User.Role.SECRETARY)
        self.client.force_authenticate(None)

        login = self.login('coordinador@iglesia.test')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn('access', login.data)

    def test_registration_cannot_choose_role(self):
        self.client.post(reverse('register'), {'email': 'nuevo@iglesia.test', 'password': PASSWORD, 'role': User.Role.ADMINISTRATOR}, format='json')
        self.assertEqual(User.objects.get(email='nuevo@iglesia.test').role, User.Role.COORDINATOR)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_cannot_change_own_role(self):
        user = create_user(User.Role.COORDINATOR)
        self.client.force_authenticate(user)
        self.client.patch(reverse('me'), {'role': User.Role.ADMINISTRATOR}, format='json')
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.COORDINATOR)

    def test_refresh_rotates_and_invalidates_previous_token(self):
        create_user(User.Role.PASTOR)
        first = self.login('pastor@iglesia.test').data['refresh']
        rotated = self.client.post(reverse('token-refresh'), {'refresh': first}, format='json')
        self.assertEqual(rotated.status_code, status.HTTP_200_OK)
        self.assertNotEqual(rotated.data['refresh'], first)
        reused = self.client.post(reverse('token-refresh'), {'refresh': first}, format='json')
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalidates_refresh_token(self):
        create_user(User.Role.PASTOR)
        session = self.login('pastor@iglesia.test').data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {session['access']}")
        logout = self.client.post(reverse('logout'), {'refresh': session['refresh']}, format='json')
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials()
        refresh = self.client.post(reverse('token-refresh'), {'refresh': session['refresh']}, format='json')
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_invalid_token(self):
        self.client.force_authenticate(create_user(User.Role.PASTOR))
        self.assertEqual(self.client.post(reverse('logout'), {'refresh': 'invalido'}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.post(reverse('logout'), {}, format='json').status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', FRONTEND_URL='http://iglesia.test')
class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = create_user(User.Role.SECRETARY)

    def reset_params(self):
        self.client.post(reverse('password-reset'), {'email': self.user.email}, format='json')
        self.assertEqual(len(mail.outbox), 1)
        return re.search(r'uid=(?P<uid>[^&]+)&token=(?P<token>\S+)', mail.outbox[0].body).groupdict()

    def test_full_reset_flow_invalidates_previous_sessions(self):
        session = self.client.post(reverse('login'), {'email': self.user.email, 'password': PASSWORD}, format='json').data
        self.assertTrue(mail.outbox == [])
        params = self.reset_params()
        self.assertIn('http://iglesia.test/reset-password', mail.outbox[0].body)

        confirm = self.client.post(reverse('password-reset-confirm'), {**params, 'password': 'NuevaClave456!'}, format='json')
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        login = self.client.post(reverse('login'), {'email': self.user.email, 'password': 'NuevaClave456!'}, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        old_refresh = self.client.post(reverse('token-refresh'), {'refresh': session['refresh']}, format='json')
        self.assertEqual(old_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

        reused = self.client.post(reverse('password-reset-confirm'), {**params, 'password': 'OtraClave789!'}, format='json')
        self.assertEqual(reused.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_does_not_reveal_unknown_email(self):
        response = self.client.post(reverse('password-reset'), {'email': 'nadie@iglesia.test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox, [])

    def test_reset_rejects_invalid_link_and_weak_password(self):
        invalid = self.client.post(reverse('password-reset-confirm'), {'uid': 'xx', 'token': 'yy', 'password': 'NuevaClave456!'}, format='json')
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        weak = self.client.post(reverse('password-reset-confirm'), {**self.reset_params(), 'password': '123'}, format='json')
        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', weak.data)


class UserAdministrationTests(APITestCase):
    def setUp(self):
        self.admin = create_user(User.Role.ADMINISTRATOR)
        self.client.force_authenticate(self.admin)

    def test_only_administrators_manage_users(self):
        for role in (User.Role.PASTOR, User.Role.SECRETARY, User.Role.TREASURER, User.Role.COORDINATOR):
            self.client.force_authenticate(create_user(role))
            self.assertEqual(self.client.get('/api/users/').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.post('/api/users/', {'email': 'x@iglesia.test', 'password': PASSWORD}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.patch(f'/api/users/{self.admin.pk}/', {'role': role}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/users/').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_change_role(self):
        create = self.client.post('/api/users/', {'email': 'tesorera@iglesia.test', 'password': PASSWORD, 'role': User.Role.TREASURER}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', create.data)
        update = self.client.patch(f"/api/users/{create.data['id']}/", {'role': User.Role.COORDINATOR}, format='json')
        self.assertEqual(update.data['role'], User.Role.COORDINATOR)

    def test_create_requires_unique_email_and_password(self):
        duplicated = self.client.post('/api/users/', {'email': 'ADMINISTRATOR@iglesia.test', 'password': PASSWORD}, format='json')
        self.assertEqual(duplicated.status_code, status.HTTP_400_BAD_REQUEST)
        missing = self.client.post('/api/users/', {'email': 'sinclave@iglesia.test'}, format='json')
        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_lock_out_themselves(self):
        create_user(User.Role.ADMINISTRATOR, 'otro@iglesia.test')
        self.assertEqual(self.client.patch(f'/api/users/{self.admin.pk}/', {'role': User.Role.PASTOR}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.patch(f'/api/users/{self.admin.pk}/', {'is_active': False}, format='json').status_code, status.HTTP_400_BAD_REQUEST)

    def test_an_administrator_always_remains(self):
        other = create_user(User.Role.ADMINISTRATOR, 'otro@iglesia.test')
        self.assertEqual(self.client.patch(f'/api/users/{other.pk}/', {'is_active': False}, format='json').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.patch(f'/api/users/{self.admin.pk}/', {'is_active': False}, format='json').status_code, status.HTTP_400_BAD_REQUEST)

    def test_regular_admin_cannot_touch_superuser(self):
        root = User.objects.create_superuser(email='root@iglesia.test', password=PASSWORD)
        response = self.client.patch(f'/api/users/{root.pk}/', {'password': 'Tomada123456!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        root.refresh_from_db()
        self.assertTrue(root.check_password(PASSWORD))

    def test_deactivation_revokes_refresh_tokens(self):
        user = create_user(User.Role.PASTOR)
        session = self.client.post(reverse('login'), {'email': user.email, 'password': PASSWORD}, format='json').data
        self.client.patch(f'/api/users/{user.pk}/', {'is_active': False}, format='json')
        refresh = self.client.post(reverse('token-refresh'), {'refresh': session['refresh']}, format='json')
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_requests(self):
        pending = User.objects.create_user(email='pendiente@iglesia.test', password=PASSWORD, is_active=False, is_approved=False)
        listed = self.client.get('/api/users/?state=pending')
        self.assertEqual([user['id'] for user in listed.data], [pending.pk])
        activate = self.client.patch(f'/api/users/{pending.pk}/', {'is_active': True}, format='json')
        self.assertEqual(activate.status_code, status.HTTP_400_BAD_REQUEST)
        reject = self.client.post(f'/api/users/{pending.pk}/reject/')
        self.assertEqual(reject.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=pending.pk).exists())

    def test_cannot_reject_or_reapprove_existing_users(self):
        user = create_user(User.Role.PASTOR)
        self.assertEqual(self.client.post(f'/api/users/{user.pk}/reject/').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.post(f'/api/users/{user.pk}/approve/').status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_choices_available_to_operational_roles_only(self):
        inactive = User.objects.create_user(email='baja@iglesia.test', password=PASSWORD, is_active=False)
        self.client.force_authenticate(create_user(User.Role.COORDINATOR))
        choices = self.client.get('/api/users/choices/')
        self.assertEqual(choices.status_code, status.HTTP_200_OK)
        self.assertNotIn(inactive.pk, [user['id'] for user in choices.data])
        self.assertNotIn('email', choices.data[0])
        self.client.force_authenticate(create_user(User.Role.TREASURER))
        self.assertEqual(self.client.get('/api/users/choices/').status_code, status.HTTP_403_FORBIDDEN)
