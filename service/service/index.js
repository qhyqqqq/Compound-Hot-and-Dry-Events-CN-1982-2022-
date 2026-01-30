const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const app = express();
const port = 5000;

// 使用中间件
app.use(cors());
app.use(express.json()); // 解析 JSON 请求体

// MySQL数据库连接配置
const connection = mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password: 'root',
  database: 'webgis',
  port: 3306
});

// 获取数据
app.get('/api/data', (req, res) => {
  const query = 'SELECT * FROM statics LIMIT 500000';
  connection.query(query, (err, results) => {
    if (err) {
      console.error("Error fetching data:", err);
      return res.status(500).json({ message: '数据库查询失败', error: err });
    }
    res.json(results);
  });
});

// 提交新数据
app.post('/api/data', (req, res) => {
  const { year, location, coordinates, count, time } = req.body;  
  const query = 'INSERT INTO statics (year, location, coordinates, count, time) VALUES (?, ?, ?, ?, ?)';
  connection.query(query, [year, location, coordinates, count, time], (err, results) => {
    if (err) {
      console.error("Error inserting data:", err);
      return res.status(500).json({ message: '插入数据失败', error: err });
    }
    res.status(201).json({
      id: results.insertId,
      year,
      location,
      coordinates,
      count,
      time
    });
  });
});

// 更新数据
app.put('/api/data/:id', (req, res) => {
  const { id } = req.params;
  if (!id) {
    return res.status(400).json({ message: '缺少ID参数' });
  }
  const { year, location, coordinates, count, time } = req.body;
  const query = 'UPDATE statics SET year = ?, location = ?, coordinates = ?, count = ?, time = ? WHERE id = ?';
  connection.query(query, [year, location, coordinates, count, time, id], (err, results) => {
    if (err) {
      console.error("Error updating data:", err);
      return res.status(500).json({ message: '更新数据失败', error: err });
    }
    res.json({ id, year, location, coordinates, count, time });
  });
});

// 删除数据
app.delete('/api/data/:id', (req, res) => {
  const { id } = req.params;
  const query = 'DELETE FROM statics WHERE id = ?';
  connection.query(query, [id], (err, results) => {
    if (err) {
      console.error("Error deleting data with ID:", id);
      console.error("Error details:", err);
      return res.status(500).json({
        message: '删除数据失败',
        error: err
      });
    }
    if (results.affectedRows === 0) {
      console.warn(`No data found to delete with ID: ${id}`);
      return res.status(404).json({ message: '未找到要删除的数据' });
    }
    console.log(`Successfully deleted data with ID: ${id}`);
    res.status(204).end();
  });
});

// 启动服务器
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
