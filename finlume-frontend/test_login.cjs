const axios = require('axios');
async function test() {
  try {
    console.log('--- SIGNUP ---');
    let res1 = await axios.post('http://localhost:8000/api/auth/register', {username: 'js_test_user2', password: 'js_password'});
    console.log(res1.status, res1.data);
    console.log('--- LOGIN ---');
    let res2 = await axios.post('http://localhost:8000/api/auth/login', {username: 'js_test_user2', password: 'js_password'});
    console.log(res2.status, res2.data);
  } catch (e) {
    if (e.response) {
      console.log(e.response.status, e.response.data);
    } else {
      console.log(e);
    }
  }
}
test();
