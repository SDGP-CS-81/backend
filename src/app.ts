import express, {Request, Response, Application} from 'express'

const app: Application = express()

app.get('/', (req: Request, res: Response) => {
  res.send('Hello world')
})

app.listen(5000, () => {
  console.log('Server is running on port 5000')
})