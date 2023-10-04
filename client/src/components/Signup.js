import React, { useEffect, useState } from "react";
import { useFormik } from "formik";
import * as yup from "yup";

function Signup({ setFamily }) {
  const [families, setFamilies] = useState([{}]);
  const [refreshPage, setRefreshPage] = useState(false);
  const [errorMsgs, setErrorMsgs] = useState([]); //use in custom validation for unique username
  //Fetch families to validate unique usernames
  async function fetchFamilies() {
    const familyFetch = await fetch("http://127.0.0.1:5555/families");
    const familyJSON = await familyFetch.json();
    setFamilies(familyJSON);
  }
  //Update family list after each successful registration
  useEffect(() => {
    fetchFamilies();
  }, [refreshPage]);

  const formSchema = yup.object().shape({
    username: yup.string().required("Must enter a username up to 16 characters").max(16),
    password: yup.string().required("Must enter a password"),
    family_name: yup.string().required("Must enter your last name (max 30 chars)").max(30),
  });

  const formik = useFormik({
    initialValues: {
      username: "",
      password: "",
      family_name: "",
    },
    validationSchema: formSchema,
    onSubmit: (values, { resetForm }) => {
      fetch("/families", {
        credentials: "include",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values, null, 2),
      }).then((r) => {
        if (r.status === 201) {
          resetForm({ values: "" });
          setRefreshPage(!refreshPage);
          setErrorMsgs([]);
        }
        if (r.status === 400) {
          setErrorMsgs(["Username already exists, please try one not listed below"]);
        }

        //Add else for error messages (i.e. unique username)
      });
    },
  });

  return (
    <div>
      {errorMsgs.map((e) => {
        return <div style={{ color: "red" }}>{e}</div>;
      })}
      <form onSubmit={formik.handleSubmit} style={{ margin: "30px" }}>
        <label htmlFor="username">Username</label>
        <br />
        <input id="username" name="username" onChange={formik.handleChange} value={formik.values.username} />
        <p style={{ color: "red" }}> {formik.errors.username}</p>
        <label htmlFor="family_name">Last Name</label>
        <br />

        <input id="family_name" name="family_name" onChange={formik.handleChange} value={formik.values.family_name} />
        <p style={{ color: "red" }}> {formik.errors.family_name}</p>

        <label htmlFor="password">password</label>
        <br />

        <input type="password" id="password" name="password" onChange={formik.handleChange} value={formik.values.password} />
        <p style={{ color: "red" }}> {formik.errors.password}</p>
        <button type="submit">Submit</button>
      </form>
      <table style={{ padding: "15px" }}>
        <tbody>
          <tr>
            <th>Reserved Usernames</th>
          </tr>
          {families == "undefined" ? (
            <tr>
              <th>Loading</th>
            </tr>
          ) : (
            families.map((family, i) => (
              <tr key={i}>
                <td>{family.family_username}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Signup;