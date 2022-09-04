const mongoose = require("mongoose");

const UptrendSchema = new mongoose.Schema({},{ strict : false });

const Uptrend = mongoose.model("Uptrend", UptrendSchema);

module.exports = Uptrend;