/* global Handlebars, createAuth0Client */
let auth0;
let token;
let perms;

/**
 * @description Flash a message in the form of a toast
 * @param {string} category - category of Bootstrap alert to flash
 * @param {string} header - header of the toast
 * @param {string} message - body of the toast
 */
function flashMessage(category, header, message) {
  const toast = document.querySelector('.toast');
  const toastHeader = document.querySelector('.toast-header');
  const toastBody = document.querySelector('.toast-body');
  toast.classList.add(`border-${category}`);
  toastHeader.firstElementChild.innerHTML = header;
  toastBody.innerHTML = message;
  $('.toast').on('hidden.bs.toast', () => {
    toast.classList.remove(`border-${category}`);
    toastHeader.firstElementChild.innerHTML = '';
    toastBody.innerHTML = '';
  });
  $('.toast').toast('show');
}

/**
 * @callback pageCallback
 * @param {number} page - number of page to retrieve data for
 */

/**
 * @description Add pagination element to page
 * @param {number} totalPages - total number of pages returned from the api
 * @param {number} page - number of the current page
 * @param {string} route - route of the current url
 * @param {pageCallback} callback - callback function to be called on a click event
 */
function addPagination(totalPages, page, route, callback) {
  const pages = [...Array(totalPages + 1).keys()];
  pages.shift();

  const paginationTemplate = Handlebars.compile(
    document.querySelector('#pagination').innerHTML
  );

  const pagination = paginationTemplate({
    pages,
    firstPage: parseInt(page, 10) === 1,
    lastPage: parseInt(page, 10) === totalPages,
  });
  const paginators = document.querySelectorAll('.pagination');
  paginators.forEach((paginator) => {
    const p = paginator;
    p.innerHTML = pagination;
  });

  const currentPages = document.querySelectorAll(`[data-page="${page}"]`);
  currentPages.forEach((pageItem) => {
    pageItem.classList.add('active');
  });

  const pageItems = document.querySelectorAll('.page-item');
  pageItems.forEach((pageItem) => {
    if (!pageItem.classList.contains('disabled')) {
      const item = pageItem;
      item.onclick = (event) => {
        event.preventDefault();
        if (!pageItem.classList.contains('active')) {
          let pageNum = event.target.parentElement.dataset.page;
          if (pageNum === 'prev') {
            pageNum = parseInt(page, 10) - 1;
          } else if (pageNum === 'next') {
            pageNum = parseInt(page, 10) + 1;
          }
          window.history.pushState(
            { route, page: pageNum },
            document.title,
            `${route}/${pageNum}`
          );
          callback(pageNum);
        }
      };
    }
  });
}

/**
 * @callback handlebarsTemplate
 * @param {Object} context - object representing the fields to be filled int
 * @return {string} string representing html to be inserted
 */

const movies = {
  /**
   * @description Create a form to create a new movie
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created form
   */
  creationForm(template) {
    const header = 'Create New Movie';
    let movieForm = template({ header });

    const div = document.createElement('div');
    div.innerHTML = movieForm;
    movieForm = div;

    movieForm.onsubmit = (event) => {
      event.preventDefault();
      const form = movieForm.lastElementChild;
      form.actors.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        movies.create(form);
      }
      form.classList.add('was-validated');
    };

    return movieForm;
  },

  /**
   * @description Create a form to edit a movie
   * @param {Object} movie - movie to edit
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created form
   */
  updateForm(movie, template) {
    const header = `Editing: ${movie.title}`;
    const { title, release_date: releaseDate, poster } = movie;
    let { actors: movieActors } = movie;
    movieActors = movieActors.map((movieActor) => movieActor.name).join(',\n');
    let movieForm = template({
      header,
      title,
      releaseDate,
      actors: movieActors,
      poster,
    });

    const div = document.createElement('div');
    div.innerHTML = movieForm;
    movieForm = div;

    movieForm.onsubmit = (event) => {
      event.preventDefault();
      const form = movieForm.lastElementChild;
      form.actors.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        movies.update(movie, form);
      }
      form.classList.add('was-validated');
    };

    return movieForm;
  },

  /**
   * @description Create a modal to view a movie
   * @param {Object} movie - movie to view
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created modal
   */
  modal(movie, template) {
    const {
      title,
      release_date: releaseDate,
      poster,
      actors: movieActors,
    } = movie;
    let movieModal = template({
      title,
      releaseDate,
      poster,
      actors: movieActors,
    });

    const div = document.createElement('div');
    div.innerHTML = movieModal;
    movieModal = div;

    if (perms.includes('update:movies')) {
      const editBtn = movieModal.querySelector('#edit-btn');
      editBtn.classList.remove('hidden');
      editBtn.onclick = () => {
        const movieFormTemplate = Handlebars.compile(
          document.querySelector('#movie-form').innerHTML
        );
        const movieForm = movies.updateForm(movie, movieFormTemplate);
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(movieForm);
      };
    }

    if (perms.includes('delete:movies')) {
      const deleteBtn = movieModal.querySelector('#delete-btn');
      deleteBtn.classList.remove('hidden');
      deleteBtn.onclick = () => {
        movies.delete(movie);
      };
    }

    return movieModal;
  },

  /**
   * @description Create a card to view a movie
   * @param {Object} movie - movie to view
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created card
   */
  card(movie, template) {
    const { poster, title, release_date: releaseDate } = movie;
    let year;
    if (releaseDate) [year] = releaseDate.split('-');
    let movieCard = template({ title, year, poster });

    const div = document.createElement('div');
    div.innerHTML = movieCard;
    movieCard = div.firstElementChild;

    movieCard.onclick = () => {
      const movieModalTemplate = Handlebars.compile(
        document.querySelector('#movie-modal').innerHTML
      );
      const movieModal = movies.modal(movie, movieModalTemplate);
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(movieModal);
      $('#modal').modal('show');
    };

    return movieCard;
  },

  /**
   * @description Fetch movies and add them to the page
   * @param {number} page - page number to retrieve movies for
   */
  add(page) {
    const navMovies = document.querySelector('#nav-movies');
    const navActors = document.querySelector('#nav-actors');
    const modal = document.querySelector('#modal');
    const createBtn = document.querySelector('#create-btn');
    navMovies.classList.add('active');
    navActors.classList.remove('active');
    modal.classList.remove('actor-modal');
    modal.classList.add('movie-modal');

    if (perms.includes('create:movies')) {
      createBtn.innerHTML = '&#10010; CREATE NEW MOVIE';
      createBtn.parentElement.classList.remove('hidden');
      createBtn.onclick = () => {
        const movieFormTemplate = Handlebars.compile(
          document.querySelector('#movie-form').innerHTML
        );
        const newMovieForm = movies.creationForm(movieFormTemplate);
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(newMovieForm);
        $('#modal').modal('show');
      };
    } else {
      createBtn.parentElement.classList.add('hidden');
    }

    fetch(`/api/movies?page=${page}`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();

        const content = document.querySelector('#content');
        content.innerHTML = '';
        const movieCardTemplate = Handlebars.compile(
          document.querySelector('#movie').innerHTML
        );
        data.movies.forEach((movie) => {
          const movieCard = movies.card(movie, movieCardTemplate);
          content.appendChild(movieCard);
        });

        const totalPages = Math.ceil(data.total_movies / 25);
        addPagination(totalPages, page, '/movies', movies.addMovies);
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });

    window.scrollTo(0, 0);
  },

  /**
   * @description Create a new movie in the db
   * @param {Object} form - form containing data for movie to create
   */
  create(form) {
    const movieActors = form.actors.value
      .split(/[\n,]+/)
      .map((actor) => actor.trim())
      .filter((actor) => actor !== '');
    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: form.title.value || null,
        release_date: form.releaseDate.value || null,
        actors: movieActors,
        poster: form.poster.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        movies.addMovies(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully created!'
        );
      })
      .catch(() => {
        form.actors.setCustomValidity('invalid');
      });
  },

  /**
   * @description Update a movie in the db
   * @param {Object} movie - movie to update
   * @param {Object} form - form containing data for movie to update
   */
  update(movie, form) {
    const movieActors = form.actors.value
      .split(/[\n,]+/)
      .map((actor) => actor.trim())
      .filter((actor) => actor !== '');
    fetch(`/api/movies/${movie.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: form.title.value || null,
        release_date: form.releaseDate.value || null,
        actors: movieActors,
        poster: form.poster.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        movies.add(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully updated!'
        );
      })
      .catch(() => {
        form.actors.setCustomValidity('invalid');
      });
  },

  /**
   * @description Delete a movie from the db
   * @param {Object} movie - movie to delete
   */
  delete(movie) {
    $('#modal').modal('hide');
    fetch(`/api/movies/${movie.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        movies.add(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully deleted!'
        );
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });
  },
};

const actors = {
  /**
   * @description Create a form to create a new actor
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created form
   */
  creationForm(template) {
    const header = 'Create New Actor';
    let actorForm = template({ header });

    const div = document.createElement('div');
    div.innerHTML = actorForm;
    actorForm = div;

    actorForm.onsubmit = (event) => {
      event.preventDefault();
      const form = actorForm.lastElementChild;

      form.movies.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        actors.create(form);
      }
      form.classList.add('was-validated');
    };

    return actorForm;
  },

  /**
   * @description Create a form to edit an actor
   * @param {Object} actor - actor to edit
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created form
   */
  updateForm(actor, template) {
    const header = `Editing: ${actor.name}`;
    const { name, birthdate, image } = actor;
    let { gender, movies: actorMovies } = actor;
    gender = {
      male: gender === 'male' ? 'selected' : '',
      female: gender === 'female' ? 'selected' : '',
    };
    actorMovies = actorMovies.map((actorMovie) => actorMovie.title).join(',\n');
    let actorForm = template({
      header,
      name,
      birthdate,
      gender,
      movies: actorMovies,
      image,
    });

    const div = document.createElement('div');
    div.innerHTML = actorForm;
    actorForm = div;

    actorForm.onsubmit = (event) => {
      event.preventDefault();
      const form = actorForm.lastElementChild;
      form.movies.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        actors.update(actor, form);
      }
      form.classList.add('was-validated');
    };

    return actorForm;
  },

  /**
   * @description Create a modal to view an actor
   * @param {Object} actor - actor to view
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created modal
   */
  modal(actor, template) {
    const { id, name, birthdate, image, movies: actorMovies } = actor;
    let { gender } = actor;
    if (gender) {
      gender = actor.gender.charAt(0).toUpperCase() + actor.gender.slice(1);
    }
    let actorModal = template({
      id,
      name,
      birthdate,
      gender,
      image,
      movies: actorMovies,
    });

    const div = document.createElement('div');
    div.innerHTML = actorModal;
    actorModal = div;

    if (perms.includes('update:actors')) {
      const editBtn = actorModal.querySelector('#edit-btn');
      editBtn.classList.remove('hidden');
      editBtn.onclick = () => {
        const actorFormTemplate = Handlebars.compile(
          document.querySelector('#actor-form').innerHTML
        );
        const actorForm = actors.updateForm(actor, actorFormTemplate);
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(actorForm);
      };
    }

    if (perms.includes('delete:actors')) {
      const deleteBtn = actorModal.querySelector('#delete-btn');
      deleteBtn.classList.remove('hidden');
      deleteBtn.onclick = () => {
        actors.delete(actor);
      };
    }

    return actorModal;
  },

  /**
   * @description Create a card to view an actor
   * @param {Object} actor - actor to view
   * @param {handlebarsTemplate} template - handlebars template to be given context and inserted
   * @return {Object} html object containing the created card
   */
  card(actor, template) {
    const { name, image, birthdate } = actor;
    let { gender } = actor;
    let age;
    if (birthdate) {
      age = new Date(Date.now() - Date.parse(birthdate)).getFullYear() - 1970;
    }
    if (gender) {
      gender = actor.gender.charAt(0).toUpperCase() + actor.gender.slice(1);
    }
    let actorCard = template({ name, age, gender, image });

    const div = document.createElement('div');
    div.innerHTML = actorCard;
    actorCard = div.firstElementChild;

    actorCard.onclick = () => {
      const actorModalTemplate = Handlebars.compile(
        document.querySelector('#actor-modal').innerHTML
      );
      const actorModal = actors.modal(actor, actorModalTemplate);
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(actorModal);
      $('#modal').modal('show');
    };

    return actorCard;
  },

  /**
   * @description Fetch actors and add them to the page
   * @param {number} page - page number to retrieve movies for
   */
  add(page) {
    const navActors = document.querySelector('#nav-actors');
    const navMovies = document.querySelector('#nav-movies');
    const modal = document.querySelector('#modal');
    const createBtn = document.querySelector('#create-btn');
    navActors.classList.add('active');
    navMovies.classList.remove('active');
    modal.classList.remove('movie-modal');
    modal.classList.add('actor-modal');

    if (perms.includes('create:actors')) {
      createBtn.innerHTML = '&#10010; CREATE NEW ACTOR';
      createBtn.parentElement.classList.remove('hidden');
      createBtn.onclick = () => {
        const actorFormTemplate = Handlebars.compile(
          document.querySelector('#actor-form').innerHTML
        );
        const newActorForm = actors.creationForm(actorFormTemplate);
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(newActorForm);
        $('#modal').modal('show');
      };
    } else {
      createBtn.parentElement.classList.add('hidden');
    }

    fetch(`/api/actors?page=${page}`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();

        const content = document.querySelector('#content');
        content.innerHTML = '';
        const actorCardTemplate = Handlebars.compile(
          document.querySelector('#actor').innerHTML
        );
        data.actors.forEach((actor) => {
          const actorCard = actors.card(actor, actorCardTemplate);
          content.appendChild(actorCard);
        });

        const totalPages = Math.ceil(data.total_actors / 25);
        addPagination(totalPages, page, '/actors', actors.add);
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });

    window.scrollTo(0, 0);
  },

  /**
   * @description Create a new actor in the db
   * @param {Object} form - form containing data for actor to create
   */
  create(form) {
    const actorMovies = form.movies.value
      .split(/[\n,]+/)
      .map((movie) => movie.trim())
      .filter((movie) => movie !== '');
    fetch('/api/actors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: form.name.value || null,
        birthdate: form.birthdate.value || null,
        gender: form.gender.value || null,
        movies: actorMovies,
        image: form.image.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        actors.add(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Actor successfully created!'
        );
      })
      .catch(() => {
        form.movies.setCustomValidity('invalid');
      });
  },

  /**
   * @description Update an actor in the db
   * @param {Object} actor - actor to update
   * @param {Object} form - form containing data for actor to update
   */
  update(actor, form) {
    const actorMovies = form.movies.value
      .split(/[\n,]+/)
      .map((movie) => movie.trim())
      .filter((movie) => movie !== '');
    fetch(`/api/actors/${actor.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: form.name.value || null,
        birthdate: form.birthdate.value || null,
        gender: form.gender.value || null,
        movies: actorMovies,
        image: form.image.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        actors.add(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Actor successfully updated!'
        );
      })
      .catch(() => {
        form.movies.setCustomValidity('invalid');
      });
  },

  /**
   * @description Delete an actor from the db
   * @param {Object} actor - actor to delete
   */
  delete(actor) {
    $('#modal').modal('hide');
    fetch(`/api/actors/${actor.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        actors.add(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Actor successfully deleted!'
        );
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });
  },
};

const updateUI = async () => {
  const loggedOut = document.querySelector('#logged-out');
  const username = document.querySelector('#username');
  const loginBtn = document.querySelector('#login-btn');
  const logoutBtn = document.querySelector('#logout-btn');

  const isAuthenticated = await auth0.isAuthenticated();
  if (isAuthenticated) {
    token = await auth0.getTokenSilently();
    perms = JSON.parse(atob(token.split('.')[1])).permissions;
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

  if (perms.includes('read:movies')) {
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
      movies.add(page);
    };

    const route = '/movies';
    const page = 1;
    window.history.pushState(
      { route, page },
      document.title,
      `${route}/${page}`
    );
    movies.add(page);
  }

  if (perms.includes('read:actors')) {
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
      actors.add(page);
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
    movies.add(page);
  } else if (route === '/actors') {
    actors.add(page);
  }
};
