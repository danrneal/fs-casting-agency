/* global createAuth0Client */

import showActors from './actors';
import showMovies from './movies';
import { auth, flashMessage } from './utils';

let auth0 = null;

const updateUI = async () => {
  const loggedOut = document.querySelector('#logged-out');
  const username = document.querySelector('#username');
  const loginBtn = document.querySelector('#login-btn');
  const logoutBtn = document.querySelector('#logout-btn');

  const isAuthenticated = await auth0.isAuthenticated();
  if (isAuthenticated) {
    auth.token = await auth0.getTokenSilently();
    auth.perms = JSON.parse(atob(auth.token.split('.')[1])).permissions;
    const user = await auth0.getUser();
    username.innerHTML = user.name;
    loggedOut.classList.add('hidden');
    loginBtn.classList.add('hidden');
    logoutBtn.classList.remove('hidden');
  } else {
    username.innerHTML = '';
    loggedOut.classList.remove('hidden');
    loginBtn.classList.remove('hidden');
    logoutBtn.classList.add('hidden');
  }

  if (auth.perms.includes('read:movies')) {
    const navMovies = document.querySelector('#nav-movies');
    navMovies.classList.remove('hidden');
    navMovies.onclick = (event) => {
      event.preventDefault();
      const route = '/movies';
      const page = 1;
      window.history.pushState(
        { route, page },
        document.title,
        `${route}/${page}`
      );
      showMovies(page);
    };

    const route = '/movies';
    const page = 1;
    window.history.pushState(
      { route, page },
      document.title,
      `${route}/${page}`
    );
    showMovies(page);
  }

  if (auth.perms.includes('read:actors')) {
    const navActors = document.querySelector('#nav-actors');
    navActors.classList.remove('hidden');
    navActors.onclick = (event) => {
      event.preventDefault();
      const route = '/actors';
      const page = 1;
      window.history.pushState(
        { route, page },
        document.title,
        `${route}/${page}`
      );
      showActors(page);
    };
  }
};

const fetchAuthConfig = () => fetch('/auth_config');

const configureClient = async () => {
  const response = await fetchAuthConfig();
  const config = await response.json();
  auth0 = await createAuth0Client({
    domain: config.domain,
    client_id: config.client_id,
    audience: config.audience,
  });
};

window.onload = async () => {
  await configureClient();

  const loginBtn = document.querySelector('#login-btn');
  loginBtn.onclick = async () => {
    await auth0.loginWithRedirect({
      redirect_uri: window.location.origin,
    });
  };

  const logoutBtn = document.querySelector('#logout-btn');
  logoutBtn.onclick = () => {
    auth0.logout({
      returnTo: window.location.origin,
    });
    flashMessage('success', '&#10004; SUCCESS', 'Successfully logged out!');
  };

  const isAuthenticated = await auth0.isAuthenticated();
  if (isAuthenticated) {
    window.history.replaceState({}, document.title, '/');
    updateUI();
    return;
  }

  const query = window.location.search;
  if (query.includes('code=') && query.includes('state=')) {
    await auth0.handleRedirectCallback();
    window.history.replaceState({}, document.title, '/');
  }

  updateUI();
};

window.onpopstate = (event) => {
  const { route, page } = event.state;
  if (route === '/movies') {
    showMovies(page);
  } else if (route === '/actors') {
    showActors(page);
  }
};
