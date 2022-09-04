const express = require("express");
require("dotenv").config();
const uptrendModal = require("./models");
const mongoose = require("mongoose");
const ObjectsToCsv = require("objects-to-csv");
const MongoClient = require("mongodb").MongoClient;

// mongoose.connect(
//     process.env.MONGODB_URL,
//     {
//         useNewUrlParser: true,
//         useUnifiedTopology: true
//     }
// );
// const db = mongoose.connection;
// db.on("error", console.error.bind(console, "connection error: "));
// db.once("open", function () {
//   console.log("Connected successfully");
// });

// const uptrend = new mongoose.Schema({

// },{ strict : false })

// const Uptrend = mongoose.model('Uptrend', uptrend);

// console.log(Uptrend.countDocuments())

// mongoose.connect(process.env.MONGODB_URL).then(() => {
//     const db = mongoose.connection.db;
//     // db.collection('uptrend').find().toArray((err, result) => {
//     //     console.log(result)
//     // });
//     const lastMonth = db.collection('uptrend').find({
//         $where: function() {
//           var currentDate = new Date();
//           var lastMonthDate = new Date(currentDate.setMonth(currentDate.getMonth() - 1));

//           return this.createdOn.getFullYear() === lastMonthDate.getFullYear()
//             && this.createdOn.getMonth() === lastMonthDate.getMonth();
//         }
//       })
// }).catch(err => console.log(err.message))

// const lastMonth = async ()=>{
//   let db =null
//   try{
//     await mongoose.connect(process.env.MONGODB_URL)
//     db = mongoose.connection.db;
//     // db.close();
//     return db.collection('uptrend').find({})
//   } catch(err){
//     console.log(err.message)
//   }
// }

// var dataToWrite;
// var fs = require('fs');

// fs.writeFile('form-tracking/formList.csv', dataToWrite, 'utf8', function (err) {
//   if (err) {
//     console.log('Some error occured - file either not saved or corrupted file saved.');
//   } else{
//     console.log('It\'s saved!');
//   }
// });

// lastMonth().then(res =>res.map(el=>{
//   let parts = el.date.split('-')
//   let res = {date: new Date(`${parts[2]}-${parts[1]}-${parts[0]}`),name:el.non_nifty.vol_based[0]?el.non_nifty.vol_based[0].name:null}
//   // console.log(res)
//   return res
// }))

// .forEach(el=>console.log(el))
// .filter(el=>{
//   var currentDate = new Date();
//   var lastMonthDate = new Date(currentDate.setMonth(currentDate.getMonth() - 1));
//   return (new Date(el.date).getFullYear() === lastMonthDate.getFullYear() && new Date(el.date).getMonth() === lastMonthDate.getMonth())
// })
// .forEach(el=>console.log(el))

// const app = express();

// app.get("/uptrend", async (request, response) => {
//   const data = await uptrendModal.find({});
//   console.log(data);
//   try {
//     response.send(data);
//   } catch (error) {
//     response.status(500).send(error);
//   }
// });

// app.listen(3000, () => console.log("Server is running"));

// Replace the uri string with your MongoDB deployment's connection string.

const uri = "";

const client = new MongoClient(process.env.MONGODB_URL);

async function run() {
  try {
    const database = client.db("tradeStrategies");

    const uptrend = database.collection("uptrend");

    // query for movies that have a runtime less than 15 minutes

    // const query = { runtime: { $lt: 15 } };

    const options = {
      // sort returned documents in ascending order by title (A->Z)

      sort: { last_modified: 1 },

      // Include only the `title` and `imdb` fields in each returned document

      projection: { _id: 0, date: 1, non_nifty: 1 },
    };

    const cursor = uptrend.find({}, options);

    // print a message if no documents were found

    if ((await cursor.count()) === 0) {
      console.log("No documents found!");
    }

    // replace console.dir with your callback to access individual elements

    let result =[]
    await cursor.forEach((el) => {
      let parts = el.date.split("-");
      let date = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
      var currentDate = new Date();
      var lastMonthDate = new Date(
        currentDate.setMonth(currentDate.getMonth() - 1)
      );
      if (date.getMonth() === lastMonthDate.getMonth()) {
        let res = {date: date.toDateString(),stock:el.non_nifty.vol_based[0]?el.non_nifty.vol_based[0].name:null}
        result.push(res)
      }
    });
    const csv = new ObjectsToCsv(result)
    await csv.toDisk('./lastmonth.csv')


    
  } finally {
    await client.close();
  }
}

run().catch(console.dir);
